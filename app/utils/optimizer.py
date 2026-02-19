import os
import numpy as np
import geopandas as gpd


# ── Clustering ────────────────────────────────────────────────────────────────

def cluster_requests(requests, radius_deg=0.003):
    """
    Group nearby requests (within ~300m) into a single representative point.
    Uses a simple greedy radius-based clustering.
    Returns a list of cluster dicts:
      { lat, lon, count, line_code, request_ids, notes }
    """
    points = [(r.lat, r.lon, r.id, r.line_code, r.note or '') for r in requests]
    visited = [False] * len(points)
    clusters = []

    for i, (lat, lon, rid, line, note) in enumerate(points):
        if visited[i]:
            continue
        cluster_pts = [(lat, lon, rid, note)]
        visited[i] = True
        for j, (lat2, lon2, rid2, line2, note2) in enumerate(points):
            if not visited[j] and line2 == line:
                dist = np.sqrt((lat - lat2) ** 2 + (lon - lon2) ** 2)
                if dist <= radius_deg:
                    cluster_pts.append((lat2, lon2, rid2, note2))
                    visited[j] = True

        # Centroid
        c_lat = np.mean([p[0] for p in cluster_pts])
        c_lon = np.mean([p[1] for p in cluster_pts])
        clusters.append({
            'lat': float(c_lat),
            'lon': float(c_lon),
            'count': len(cluster_pts),
            'line_code': line,
            'request_ids': [p[2] for p in cluster_pts],
            'notes': [p[3] for p in cluster_pts if p[3]],
        })

    return clusters


# ── Existing stops from shapefile ─────────────────────────────────────────────

def get_existing_stops(line_code: str, data_dir: str) -> list:
    """Return the existing ordered stops for a line from the shapefile."""
    try:
        # Load stops
        stops = gpd.read_file(os.path.join(data_dir, 'fermate_bus.shp'))
        if stops.crs and stops.crs.to_epsg() != 4326:
            stops = stops.to_crs('EPSG:4326')
        line_stops = stops[stops['codLinea'] == line_code].copy()
        
        if line_stops.empty:
            return []

        # Load line geometry to order stops along it
        lines = gpd.read_file(os.path.join(data_dir, 'linee_bus.shp'))
        if lines.crs and lines.crs.to_epsg() != 4326:
            lines = lines.to_crs('EPSG:4326')
        
        # Get all arcs for this line and merge them into a single geometry
        line_geom = lines[lines['codLinea'] == line_code].unary_union
        
        if line_geom.is_empty:
            # Fallback if no line geometry found: just return stops unordered
            result = []
            for _, row in line_stops.iterrows():
                result.append({
                    'lat': float(row.geometry.y),
                    'lon': float(row.geometry.x),
                    'name': str(row.get('nomeFermat', 'Fermata')),
                    'is_new': False,
                    'is_approved': False,
                })
            return result

        # Project stops onto the line to find their relative position
        line_stops['dist'] = line_stops.geometry.map(lambda p: line_geom.project(p))
        line_stops = line_stops.sort_values('dist')

        result = []
        for _, row in line_stops.iterrows():
            result.append({
                'lat': float(row.geometry.y),
                'lon': float(row.geometry.x),
                'name': str(row.get('nomeFermat', 'Fermata')),
                'is_new': False,
                'is_approved': False,
            })
        return result
    except Exception as e:
        print(f"get_existing_stops error: {e}")
        return []


# ── Route with approved stops merged in ───────────────────────────────────────

def get_full_route(line_code: str, data_dir: str, approved_stops: list) -> list:
    """
    Merge shapefile stops with DB-approved stops, inserting each approved stop
    at its stored insert_after index.
    """
    base = get_existing_stops(line_code, data_dir)

    # Sort approved stops by insert_after descending so insertions don't shift indices
    sorted_approved = sorted(approved_stops, key=lambda s: (s.insert_after or 0), reverse=True)
    for s in sorted_approved:
        idx = min(s.insert_after or len(base), len(base))
        base.insert(idx, {
            'lat': s.lat,
            'lon': s.lon,
            'name': 'Nuova fermata ✓',
            'is_new': True,
            'is_approved': True,
        })
    return base


# ── Cheapest-insertion optimizer ──────────────────────────────────────────────

def optimize_route(line_code: str, new_lat: float, new_lon: float,
                   data_dir: str, approved_stops: list = None) -> tuple:
    """
    Find the best insertion position for a new stop.
    Returns (new_route_list, insert_after_index).
    """
    try:
        base = get_full_route(line_code, data_dir, approved_stops or [])
        if not base:
            stop = {'lat': new_lat, 'lon': new_lon, 'name': 'Nuova fermata', 'is_new': True, 'is_approved': False}
            return [stop], 0

        new_point = np.array([new_lat, new_lon])
        best_idx = 0
        best_cost = float('inf')

        for i in range(len(base)):
            p1 = np.array([base[i]['lat'], base[i]['lon']])
            p2 = np.array([base[(i + 1) % len(base)]['lat'],
                           base[(i + 1) % len(base)]['lon']])
            cost = (np.linalg.norm(p1 - new_point) +
                    np.linalg.norm(new_point - p2) -
                    np.linalg.norm(p1 - p2))
            if cost < best_cost:
                best_cost = cost
                best_idx = i + 1

        new_stop = {'lat': new_lat, 'lon': new_lon, 'name': 'Nuova fermata ✓', 'is_new': True, 'is_approved': False}
        route = base[:best_idx] + [new_stop] + base[best_idx:]
        return route, best_idx

    except Exception as e:
        print(f"optimize_route error: {e}")
        stop = {'lat': new_lat, 'lon': new_lon, 'name': 'Nuova fermata', 'is_new': True, 'is_approved': False}
        return [stop], 0

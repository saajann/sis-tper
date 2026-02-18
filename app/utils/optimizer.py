import os
import geopandas as gpd
import numpy as np


def get_existing_stops(line_code: str, data_dir: str) -> list:
    """Return the existing ordered stops for a line as a list of dicts."""
    try:
        stops = gpd.read_file(os.path.join(data_dir, 'fermate_bus.shp'))
        if stops.crs and stops.crs.to_epsg() != 4326:
            stops = stops.to_crs('EPSG:4326')
        line_stops = stops[stops['codLinea'] == line_code]
        result = []
        for _, row in line_stops.iterrows():
            result.append({
                'lat': row.geometry.y,
                'lon': row.geometry.x,
                'name': row.get('nomeFermat', 'Fermata'),
                'is_new': False,
            })
        return result
    except Exception as e:
        print(f"get_existing_stops error: {e}")
        return []


def optimize_route(line_code: str, new_lat: float, new_lon: float, data_dir: str) -> list:
    """
    Find the best insertion position for a new stop in the existing sequence
    using a cheapest-insertion heuristic.
    Returns the new ordered list of stops.
    """
    try:
        existing = get_existing_stops(line_code, data_dir)
        if not existing:
            return [{'lat': new_lat, 'lon': new_lon, 'name': 'Nuova fermata', 'is_new': True}]

        new_point = np.array([new_lat, new_lon])
        best_idx = 0
        best_cost = float('inf')

        for i in range(len(existing)):
            p1 = np.array([existing[i]['lat'], existing[i]['lon']])
            p2 = np.array([existing[(i + 1) % len(existing)]['lat'],
                           existing[(i + 1) % len(existing)]['lon']])
            cost = (np.linalg.norm(p1 - new_point) +
                    np.linalg.norm(new_point - p2) -
                    np.linalg.norm(p1 - p2))
            if cost < best_cost:
                best_cost = cost
                best_idx = i + 1

        new_stop = {'lat': new_lat, 'lon': new_lon, 'name': 'Nuova fermata ✓', 'is_new': True}
        return existing[:best_idx] + [new_stop] + existing[best_idx:]

    except Exception as e:
        print(f"optimize_route error: {e}")
        return [{'lat': new_lat, 'lon': new_lon, 'name': 'Nuova fermata', 'is_new': True}]

import os
import geopandas as gpd
from flask import Blueprint, render_template, request, jsonify
from app_logic import db
from app_logic.models import StopRequest, ApprovedStop
from app_logic.utils.map_utils import create_map
from app_logic.utils.optimizer import get_full_route

main = Blueprint('main', __name__)

def _data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def _get_all_lines():
    lines_df = gpd.read_file(os.path.join(_data_dir(), 'linee_bus.shp'))
    return sorted(lines_df['codLinea'].unique().tolist())

# ── Citizen map ───────────────────────────────────────────────────────────────

@main.route('/')
def index():
    layers_param = request.args.get('layers', 'lines,stops')
    enabled_layers = layers_param.split(',')

    bus_lines_param = request.args.get('bus_lines', '')
    selected_bus_lines = bus_lines_param.split(',') if bus_lines_param else []

    m = create_map(enabled_layers=enabled_layers, selected_lines=selected_bus_lines)
    map_html = m.get_root().render()
    all_lines = _get_all_lines()

    return render_template('index.html',
                           map_html=map_html,
                           enabled_layers=enabled_layers,
                           all_lines=all_lines,
                           selected_bus_lines=selected_bus_lines)

# ── Submit stop request ───────────────────────────────────────────────────────

@main.route('/request-stop', methods=['POST'])
def request_stop():
    data = request.get_json()
    line_code = data.get('line_code', '').strip()
    lat = data.get('lat')
    lon = data.get('lon')
    note = data.get('note', '').strip()[:300]

    preferred_days = data.get('preferred_days', '').strip()
    preferred_time = data.get('preferred_time', '').strip()

    if not line_code or lat is None or lon is None:
        return jsonify({'ok': False, 'error': 'Dati mancanti'}), 400

    stop_req = StopRequest(
        line_code=line_code,
        lat=lat,
        lon=lon,
        note=note,
        preferred_days=preferred_days,
        preferred_time=preferred_time
    )
    db.session.add(stop_req)
    db.session.commit()
    return jsonify({'ok': True, 'id': stop_req.id})

# ── Public live route API ──────────────────────────────────────────────────────

@main.route('/api/route/<line_code>')
def api_route(line_code):
    """
    Return the live route for a bus line, merging shapefile stops with
    any approved stops from the DB. Used by the citizen map to update
    dynamically after admin approvals.
    """
    data_dir = _data_dir()
    approved = ApprovedStop.query.filter_by(line_code=line_code).all()
    route = get_full_route(line_code, data_dir, approved)
    # Also include pending cluster count for the line
    pending_count = StopRequest.query.filter_by(line_code=line_code, status='pending').count()
    return jsonify({
        'ok': True,
        'line_code': line_code,
        'stops': route,
        'pending_count': pending_count,
    })

# ── Pending heatmap data ───────────────────────────────────────────────────────

@main.route('/api/pending-points')
def api_pending_points():
    """Return all pending request points (for citizen map context layer)."""
    pending = StopRequest.query.filter_by(status='pending').all()
    return jsonify({
        'ok': True,
        'points': [{'lat': r.lat, 'lon': r.lon, 'line': r.line_code} for r in pending],
    })

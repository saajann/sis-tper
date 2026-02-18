import os
import geopandas as gpd
from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import StopRequest
from app.utils.map_utils import create_map

main = Blueprint('main', __name__)

def _get_all_lines():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    lines_df = gpd.read_file(os.path.join(data_dir, 'linee_bus.shp'))
    return sorted(lines_df['codLinea'].unique().tolist())

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


@main.route('/request-stop', methods=['POST'])
def request_stop():
    data = request.get_json()
    line_code = data.get('line_code', '').strip()
    lat = data.get('lat')
    lon = data.get('lon')
    note = data.get('note', '').strip()[:300]

    if not line_code or lat is None or lon is None:
        return jsonify({'ok': False, 'error': 'Dati mancanti'}), 400

    stop_req = StopRequest(line_code=line_code, lat=lat, lon=lon, note=note)
    db.session.add(stop_req)
    db.session.commit()

    return jsonify({'ok': True, 'id': stop_req.id})

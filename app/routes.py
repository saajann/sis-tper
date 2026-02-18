from flask import Blueprint, render_template, request
from app.utils.map_utils import create_map

main = Blueprint('main', __name__)

@main.route('/')
def index():
    layers_param = request.args.get('layers', 'lines,stops')
    enabled_layers = layers_param.split(',')
    
    bus_lines_param = request.args.get('bus_lines', '')
    selected_bus_lines = bus_lines_param.split(',') if bus_lines_param else []
    
    m = create_map(enabled_layers=enabled_layers, selected_lines=selected_bus_lines)
    map_html = m.get_root().render()
    
    # Get all unique lines for the filter UI
    import os
    import geopandas as gpd
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    lines_df = gpd.read_file(os.path.join(data_dir, 'linee_bus.shp'))
    all_lines = sorted(lines_df['codLinea'].unique().tolist())
    
    return render_template('index.html', 
                         map_html=map_html, 
                         enabled_layers=enabled_layers, 
                         all_lines=all_lines,
                         selected_bus_lines=selected_bus_lines)

import folium

import geopandas as gpd

import os



def create_map(enabled_layers=None, selected_lines=None):

    if enabled_layers is None:

        enabled_layers = ['lines', 'stops'] # Default lightweight layers



    # Center map on Bologna

    m = folium.Map(location=[44.494887, 11.3426163], zoom_start=13)



    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

    # Fallback: if that path doesn't exist, try one level up (app/utils → app → project root)

    if not os.path.isdir(data_dir):

        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

   

    # Load shapefiles (add error handling as needed)

    try:

        if 'buildings' in enabled_layers:

            buildings = gpd.read_file(os.path.join(data_dir, 'edifici.shp'))

            if buildings.crs != 'EPSG:4326':

                buildings = buildings.to_crs('EPSG:4326')

            buildings['geometry'] = buildings.simplify(tolerance=0.0001, preserve_topology=True)

            folium.GeoJson(buildings, name='Buildings', style_function=lambda x: {'color': 'gray', 'weight': 1}).add_to(m)



        if 'roads' in enabled_layers:

            roads = gpd.read_file(os.path.join(data_dir, 'strade.shp'))

            if roads.crs != 'EPSG:4326':

                roads = roads.to_crs('EPSG:4326')

            roads['geometry'] = roads.simplify(tolerance=0.0001, preserve_topology=True)

            folium.GeoJson(roads, name='Roads', style_function=lambda x: {'color': 'black', 'weight': 2}).add_to(m)



        if 'lines' in enabled_layers:

            lines = gpd.read_file(os.path.join(data_dir, 'linee_bus.shp'))

            if lines.crs != 'EPSG:4326':

                lines = lines.to_crs('EPSG:4326')

           

            if selected_lines:

                lines = lines[lines['codLinea'].isin(selected_lines)]



            folium.GeoJson(

                lines,

                name='Bus Lines',

                style_function=lambda x: {'color': 'blue', 'weight': 3},

                tooltip=folium.GeoJsonTooltip(fields=['codLinea'], aliases=['Route Line:'])

            ).add_to(m)

       

        if 'stops' in enabled_layers:

            stops = gpd.read_file(os.path.join(data_dir, 'fermate_bus.shp'))

            if stops.crs != 'EPSG:4326':

                stops = stops.to_crs('EPSG:4326')

           

            if selected_lines:

                stops = stops[stops['codLinea'].isin(selected_lines)]



            for idx, row in stops.iterrows():

                folium.CircleMarker(

                    location=[row.geometry.y, row.geometry.x],

                    radius=3,

                    color='red',

                    fill=True,

                    fill_color='red',

                    popup=f"Stop: {row.get('nomeFermat', 'N/A')}<br>Lines: {row.get('codLinea', 'N/A')}"

                ).add_to(m)



    except Exception as e:

        print(f"Error loading shapefiles: {e}")



    folium.LayerControl().add_to(m)
    
    return m
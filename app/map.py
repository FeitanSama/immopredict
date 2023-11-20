import pydeck as pdk
import pandas as pd 
import geopandas as gpd
from shapely import wkt
from babel.numbers import format_currency

def get_map(dataframe, initial_longitude, initial_latitude):
    dataframe = dataframe.copy(deep=True)
    dataframe['valeurfonc'] = dataframe['valeurfonc'].map(lambda x: format_currency(x, currency="EUR", locale="fr_FR"))
    dataframe['geometry'] = dataframe['geometry'].apply(wkt.loads)
    dataframe = gpd.GeoDataFrame(dataframe, geometry='geometry')
    geojson = pdk.Layer(
        "GeoJsonLayer",
        data=dataframe,
        opacity=0.4,
        stroked=False,
        filled=True,
        extruded=True,
        pickable=True,
        wireframe=True,
        get_elevation="5",
        get_fill_color="[51, 153, 255]",
        get_line_color=[0, 0, 0],
    )

    tooltip={
        'html': """ 
                <b>Date de mutation :</b> {anneemut}-{moismut}-{jourmut} <br/>
                <br/>
                <b>Nature de la mutation :</b> {libnatmut} <br/> 
                <b>Vefa</b> {vefa} <br/> 
                <b>Type du bien :</b> {codtypbien} - {libtypbien}<br/>
                <br/>
                <b>Surface du batie :</b> {sbati} m² <br/>
                <b>Surface du terrain :</b> {sterr} m² <br/> 
                <br/>
                <b>Prix du bien :</b> {valeurfonc}<br/> 
                """,
        'style': {
            'color': 'white'
        }
    }

    map = pdk.Deck(
        map_style="road",
        initial_view_state=pdk.ViewState(
            latitude=initial_latitude,
            longitude=initial_longitude,
            zoom=17,
            pitch=50,
        ),
        layers=[geojson],
        tooltip=tooltip
    )
    return map
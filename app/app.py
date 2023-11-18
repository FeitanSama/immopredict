import utils
import map
import json
import streamlit as st
import pydeck as pdk
import plotly.express as px
import pandas as pd
import requests 
import geopandas as gpd
import numpy
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def apidf(url_endpoint, token=None):
    HEADERS = {
        "Content-Type": "application/json",
    }
    if token:
        HEADERS["Authorization"] = "Token " + token
    response = requests.get(
        url_endpoint,
        headers=HEADERS,
    )  
    if response.status_code == 200:
      return response.json()
    return None

def load_page():
    st.set_page_config(
        page_title = "Immopredict",             # Page Title
        page_icon = "app/assets/favicon.png",   # Page Icon 
        layout = "wide",                        # Page layout 
        initial_sidebar_state = "auto",         # Sidebar init status
    )

load_page()

# SIDEBAR SETUP
input_addresse = st.sidebar.text_input('Adresse', '3 rue waldeck rousseau 946')

option_input = st.sidebar.selectbox(
    'Type de selection',
    ('BBOX', 'INSEE'),
    index=0
)

with st.sidebar.expander("Autres parametres de recherches"):

    st.title("ANNEE MUTATION")
    annee_min, annee_max = st.columns(2)
    with annee_min:
        st.number_input('ANNEE MIN')
    with annee_max:
        st.number_input('ANNEE MAX')

    st.title("BBOX")
    bbox_x, bbox_y = st.columns(2)
    with bbox_x:
        st.number_input('BBOX-X')
    with bbox_y:
        st.number_input('BBOX-Y')
    
    st.title("Surface du Bati")
    sbati_min, sbati_max = st.columns(2)
    with sbati_min:
        st.number_input('SBATI MIN')
    with sbati_max:
        st.number_input('SBATI MAX')

    st.title("Surface du Terrain")
    sterr_min, sterr_max = st.columns(2)
    with sterr_min:
        st.number_input('STERR MIN')
    with sterr_max:
        st.number_input('STERR MAX')

search_button = st.sidebar.button('Search')

    

# PROCESS START
if search_button:
    selected_adresse = utils.get_list_of_adresses(input_addresse,1)['features'][0]['properties']['label']
    adresse_info = utils.get_info_of_specific_adresse(selected_adresse)

    x = adresse_info['features'][0]['geometry']['coordinates'][0]
    y = adresse_info['features'][0]['geometry']['coordinates'][1]
    code_insee = adresse_info['features'][0]['properties']['citycode']
    nom = adresse_info['features'][0]['properties']['city']

    fdf= pd.DataFrame()
    i = 1
    while True:
        map_adds = gpd.read_file(f"https://apidf-preprod.cerema.fr/dvf_opendata/geomutations/?in_bbox={x - 0.007},{y - 0.007},{x + 0.007},{y + 0.007}&page={i}&page_size=15000")
        fdf = pd.concat([fdf, map_adds])
        print(i,"-",map_adds.shape[0])
        i += 1
        if map_adds.shape[0] < 500:
            break

    subs = fdf[fdf['l_codinsee'].str.contains(f'{int(code_insee)}', regex=False)]

    geojson = pdk.Layer(
        "GeoJsonLayer",
        data=subs,
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
                <b>Date de mutation :</b> {datemut} <br/>
                <b>Nature de la mutation :</b> {libnatmut} <br/> 
                <b>Type/Code du bien :</b> {libtypbien} - {codtypbien}<br/>
                <b>Prix du bien :</b> {valeurfonc} <br/> 
                <b>Surface du bati :</b> {sbati} <br/> 
                <b>Vefa</b> {vefa} <br/> 
                <b>code insee</b> {l_codinsee}
                """,
        'style': {
            'color': 'white'
        }
    }

    st.pydeck_chart(pdk.Deck(
        map_style="road",
        initial_view_state=pdk.ViewState(
            latitude=adresse_info['features'][0]['geometry']['coordinates'][1],
            longitude=adresse_info['features'][0]['geometry']['coordinates'][0],
            zoom=17,
            pitch=50,
        ),
        layers=[geojson],
        tooltip=tooltip
    ))

    BASE_URL_API = "https://apidf-preprod.cerema.fr"

    url = BASE_URL_API + f"/indicateurs/dv3f/communes/annuel/{code_insee}"
    url2 = BASE_URL_API + f"/indicateurs/conso_espace/communes/{code_insee}"
    url3 = BASE_URL_API + f"/dvf_opendata/mutations/?code_insee={code_insee}&page_size=1000&anneemut_min=2018&codtypbien=111"

    response  = apidf(url)
    indicateurs = pd.DataFrame.from_dict(response["results"])

    response2  = apidf(url2)
    indicateurs2 = pd.DataFrame.from_dict(response2["results"])

    # Edition du graphique
    fig = px.bar(indicateurs, 
                x='annee', 
                y=['nbtrans_cod111', 'nbtrans_cod121'], 
                title = f"Evolution annuelle du nombre de ventes de logements individuels à {nom}", 
                labels={"annee" : "Année de mutation", 
                        "value" : "Nombre de ventes",},
                )
    noms={"nbtrans_cod111": "Maison individuelle", 
        "nbtrans_cod121": "Appartement individuel"}
    fig.update_layout(legend_title_text="Nombre de ventes")
    fig.for_each_trace(lambda t: t.update(hovertemplate = t.hovertemplate.replace(t.name, noms[t.name]), name=noms[t.name]))

    # Edition du graphique
    fig2 = px.line(indicateurs, 
                x='annee', 
                y=['pxm2_median_mmx', 'pxm2_median_amx'], 
                title = f"Evolution annuelle du prix médian des logements sur {nom}", 
                range_y=[0, 5500],
                labels={"annee" : "Année de mutation", 
                        "value" : "Prix en €/m2",},
                )
    noms={"pxm2_median_mmx": "Maison moyenne (entre 90 et 130 m2)", 
        "pxm2_median_amx": "Appartement ancien (T3 et T4)"}
    fig2.update_layout(legend_title_text="Prix médian au mètre carré")
    fig2.for_each_trace(lambda t: t.update(hovertemplate = t.hovertemplate.replace(t.name, noms[t.name]), name=noms[t.name]))



    fig3 = px.bar(indicateurs2, 
                x='annee', 
                y=['naf_arti', "conso_hab",  "conso_act"], 
                title = f"Evolution annuelle de la consommation d'espaces à {nom}", 
                labels={"annee" : "Année", 
                        "value" : "Surface (m2)",},
                barmode = "group",
                )
    noms={"naf_arti": "totale", "conso_act": "liée à l'activité", "conso_hab": "liée à l'habitat"}
    fig3.update_layout(legend_title_text="Consommation d'espaces")
    fig3.for_each_trace(lambda t: t.update(hovertemplate = t.hovertemplate.replace(t.name, noms[t.name]), name=noms[t.name]))
    

    pages = []

    while True:
        response = apidf(url3) 
        mutations = pd.DataFrame.from_dict(response["results"])
        pages.append(mutations)
        if not response["next"]:
            break
        url3 = response["next"]

    # concaténation des pages et affichage graphique
    mutations = pd.concat(pages)
    mutations["valeurfonc"] = mutations["valeurfonc"].astype(float)
    fig4 = px.violin(mutations, 
                    y="valeurfonc", 
                    x="anneemut", 
                    color="anneemut", 
                    box=True, 
                    title = f"Distribution annuelle des prix des ventes de maison à partir de 2018 à {nom}", 
                    labels={"annee" : "Année", 
                            "valeurfonc" : "Prix en €",},)
    fig4.update_layout(legend_title_text="Année de mutation")

    graph1_col, graph2_col = st.columns(2)

    with graph1_col: 
        st.plotly_chart(fig, use_container_width=True)

    with graph2_col: 
        st.plotly_chart(fig2, use_container_width=True)


    graph3_col, graph4_col = st.columns(2)

    with graph3_col:
        st.plotly_chart(fig3, use_container_width=True)

    with graph4_col: 
        st.plotly_chart(fig4, use_container_width=True)
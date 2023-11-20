# ----------------------------
#       IMPORTS MODULES
# ----------------------------

# CUSTOM MODULES
import utils
import map
import data

import os
import json
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans


# ----------------------------
#       PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title = "Immopredict",             # Page Title
    page_icon = "app/assets/images/favicon.png",   # Page Icon 
    layout = "wide",                        # Page layout 
    initial_sidebar_state = "auto",         # Sidebar init status
)
cwd = os.getcwd()

# ----------------------------
#       SIDEBAR CONFIG
# ----------------------------

st.sidebar.title("PAGES")

pages = [
    'ABOUT',
    'GET DATA',
    'DASHBOARD',
    'BUILD ML/DL'
]

# Page selection
page = st.sidebar.selectbox('Select a page', pages)

# ----------------------------
#       ABOUT CONFIG
# ----------------------------
if page == 'ABOUT':
    col1,col2,col3 = st.columns([2,6,2])
    with col2:
        st.image('app/assets/images/image.jpg',width=640)
    st.write("""

Projet Immobilier Intelligent : IMMOPREDICT

Notre projet révolutionnaire allie les capacités du machine learning et du deep learning en Python pour créer une plateforme novatrice de visualisation 3D et de prédiction des prix immobiliers. En exploitant les données de l'API des Déclarations de Valeurs Foncières (DVF), notre modèle analyse les tendances du marché et les caractéristiques des quartiers, permettant aux vendeurs de fixer des prix compétitifs et aux acheteurs de prendre des décisions éclairées.

Points Clés :

Analyse des Données : Utilisation d'algorithmes de machine learning pour analyser les données historiques des transactions immobilières.

Deep Learning : Intégration de réseaux neuronaux profonds pour extraire des modèles complexes et améliorer la précision des prédictions.

Visualisation 3D : Création d'une expérience immersive permettant aux utilisateurs d'explorer virtuellement les propriétés et les quartiers.

Prédiction des Prix : Modèles de prédiction basés sur des données spécifiques à chaque bien, offrant aux vendeurs la possibilité de fixer des prix compétitifs et aux acheteurs une évaluation précise des offres.

Avantages : Les vendeurs bénéficient d'une fixation de prix compétitive, tandis que les acheteurs accèdent à des informations détaillées pour des décisions informées.

Ce projet représente une avancée significative, promettant de transformer l'expérience immobilière en offrant transparence, précision, et innovation à l'ensemble du marché immobilier.""")


if page == "GET DATA":

    st.sidebar.title('DATA PARAMETERS')

    with st.sidebar.expander("PARAMETERS"):

        option_input = st.selectbox(
            'Type de selection',
            ('BBOX', 'INSEE'),
            index=0
        )

        if option_input =='BBOX':
            input_addresse = st.text_input('Adresse', '3 rue waldeck rousseau 946')
            st.title("BBOX (deg)")
            st.write("Emprise rectangulaire (via Longitude min,Latitude min,Longitude max,Latitude max). L'emprise demandée ne doit pas excéder un carré de 0.02 deg. x 0.02 deg.")
            bbox_val = st.number_input('BBOX',value=0.014,min_value = 0.001, max_value = 0.021, step= 0.001, format="%.3f")
        
        if option_input =='INSEE':
            st.title("INSEE")
            st.write("Code INSEE communal ou d'arrondissement municipal (il est possible d'en demander plusieurs (10 maximum), séparés par des virgules, dans le même département)")
            insee_val = st.text_input('CODE','94022')

        search_button = st.sidebar.button('Search')
        m = st.markdown("""
        <style> 
            div.stButton > button:first-child {
                width: 23em;
            }
        </style>
        """, unsafe_allow_html=True)

    if search_button:
        
        f= open("app/data/data.txt","w+")
        selected_adresse = utils.get_list_of_adresses(input_addresse,1)['features'][0]['properties']['label']
        f.write(f"{selected_adresse}\n")
        adresse_info = utils.get_info_of_specific_adresse(selected_adresse)
        f.write(f"{adresse_info}\n")
        x = adresse_info['features'][0]['geometry']['coordinates'][0]
        f.write(f"{x}\n")
        y = adresse_info['features'][0]['geometry']['coordinates'][1]
        f.write(f"{y}\n")
        code_insee = adresse_info['features'][0]['properties']['citycode']
        f.write(f"{code_insee}\n")
        nom = adresse_info['features'][0]['properties']['city']
        f.write(f"{nom}\n")
        f.close()
        st.write("Merci d'attendre la fin du chargement pour passer à l'étape suivante")

        if option_input == 'BBOX':
            st.write("Vous avez choisis la méthode",option_input,"avec l'argument",bbox_val)
            immodf = data.get_data(option_input,bbox_val,x,y)
        else:
            st.write("Vous avez choisis la méthode",option_input,"avec l'argument",insee_val)
            immodf = data.get_data(option_input,insee_val,0,0)
        st.success("La dataframe a été enregistré, veuillez changer la page sur PREPROCESS DATA pour modifier les données de votre choix")
        immodf.to_csv(cwd+"/app/data/out.csv")

if page == "DASHBOARD":

    immodf = pd.read_csv("app/data/out.csv")
    immo_pred,immo_viz = data.process_data(immodf)

    st.sidebar.title('DATA PARAMETERS')

    with st.sidebar.expander("PARAMETERS"):

        biens_selected = st.multiselect(
            'Type de selection',
            immo_viz['libtypbien'].unique(),
            default = ["UNE MAISON", "UN APPARTEMENT","ACTIVITE"]
        )

    immo_viz = immo_viz[immo_viz['libtypbien'].isin(biens_selected)]

    f = open("app/data/data.txt", "r")
    selected_adresse = f.readline()
    adresse_info = f.readline()
    x = float(f.readline())
    y = float(f.readline())
    code_insee = f.readline()
    nom = f.readline()
    f.close()

    st.pydeck_chart(map.get_map(immo_viz,x,y))

    immo_viz["pricem2"] = immo_viz['valeurfonc']/immo_viz['sbati']
    df = immo_viz.groupby(['anneemut','libtypbien'])['pricem2'].mean().reset_index()
    fig3 = px.bar(
        df,
        x= "anneemut", 
        y= "pricem2",
        color="libtypbien", 
        barmode='group',
        title = "Evolution annuelle du m2 des logements en fonction de l'annee et du type de bien",
        labels={"anneemut" : "Année de mutation","pricem2" : "Prix en €/m2",}
    )
    st.plotly_chart(fig3, use_container_width=True)

    plot, plot1 = st.columns(2)

    with plot:
        df = immo_viz.groupby(['anneemut','libtypbien'])['valeurfonc'].sum().reset_index()
        fig = px.bar(
            df,
            x= "anneemut", 
            y= "valeurfonc",
            color="libtypbien", 
            barmode='group',
            title = "Cout total des mutations de biens en fonction de l'annee et du type de bien",
            labels={"anneemut" : "Année de mutation","valeurfonc" : "Prix total en €",}
        )
        st.plotly_chart(fig, use_container_width=True)

    with plot1:
        df = immo_viz.groupby(['anneemut','libtypbien'])['valeurfonc'].mean().reset_index()
        fig2 = px.bar(
            df,
            x= "anneemut", 
            y= "valeurfonc",
            color="libtypbien", 
            barmode='group',
            title = "Evolution annuelle du prix moyen des logements en fonction de l'annee et du type de bien",
            labels={"anneemut" : "Année de mutation","valeurfonc" : "Prix moyen en €",}
        )
        st.plotly_chart(fig2, use_container_width=True)

    plot2, plot3 = st.columns(2)

    with plot2:
        df = immo_viz.groupby(['libtypbien'])['vefa'].sum().reset_index()
        fig4 = px.pie(df, values='vefa', names='libtypbien', title='VEFA')
        st.plotly_chart(fig4, use_container_width=True)

    with plot3:
        df = immo_viz['libtypbien'].value_counts().reset_index()
        fig5 = px.pie(df, values='libtypbien', names='index', title='REPARTITION DES BIENS')
        st.plotly_chart(fig5, use_container_width=True)

    immo_pred.to_csv(cwd+"/app/data/pred.csv")


if page == 'BUILD ML/DL':

    st.sidebar.title('DATA PARAMETERS')

    with st.sidebar.expander("PARAMETERS"):

        vefa_val = st.number_input("VEFA 0 or 1")
        nb_par_val = st.number_input("NOMBRE DE PARCELLE 1 par default")
        nb_par_mut_val = st.number_input("NOMBRE DE PARCELLE MUTATION 0 par default")
        sterr_val = st.number_input("SURFACE DU TERRAIN")
        sbati_val = st.number_input("SURFACE DU BATI")
        nbvolmut_val = st.number_input("NB DE VOLUME PAR MUTATION 0 par default")
        nblocmut_val = st.number_input("NB DE LOCAUX PAR MUTATION 0 par default")
        codtypbien_val = st.number_input("CODE DU TYPE DU BIEN (14 ACTIVITE, 121 APPARTEMENT, 111 MAISON, 229 TERRAIN)")

        launch = st.button('Lauch predict')

    data = pd.read_csv("app/data/pred.csv")
    data.drop(['Unnamed: 0','libnatmut','moismut','jourmut'], axis = 1, inplace = True)
    data.dropna(inplace=True)

    y = data['valeurfonc']
    X = data.drop(['valeurfonc'], axis = 1)

    st.dataframe(data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', LinearRegression())
    ])

    pipeline.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = pipeline.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    st.write(f'mean square error : {mse}')

    if launch :
        predict_val = pd.DataFrame({
            'vefa': vefa_val,
            'nbpar': nb_par_val,
            'nbparmut': nb_par_mut_val,
            'sterr': sterr_val,
            'nbvolmut': nbvolmut_val,
            'nblocmut': nblocmut_val,
            'sbati': sbati_val,
            'codtypbien': codtypbien_val
        }, index=[0])

        prix_predits = pipeline.predict(predict_val)
        st.write(prix_predits[0])
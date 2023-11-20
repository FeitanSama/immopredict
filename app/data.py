import ssl
import requests
import pandas as pd
import geopandas as gpd

def get_data(choice, params,x,y):

    ssl._create_default_https_context = ssl._create_unverified_context
    df= pd.DataFrame()
    i = 1
    if choice == "BBOX":
        while True:
            map_adds = gpd.read_file(f"https://apidf-preprod.cerema.fr/dvf_opendata/geomutations/?in_bbox={x - params/2},{y - params/2},{x + params/2},{y + params/2}&page={i}&page_size=10000")
            df = pd.concat([df, map_adds])
            print(i,"-",map_adds.shape[0])
            i += 1
            if map_adds.shape[0] < 500:
                break
        return df
    else:
        while True:
            map_adds = gpd.read_file(f"https://apidf-preprod.cerema.fr/dvf_opendata/geomutations/?code_insee={params}&page={i}&page_size=10000")
            df = pd.concat([df, map_adds])
            print(i,"-",map_adds.shape[0])
            i += 1
            if map_adds.shape[0] < 500:
                break
        return df

def process_data(dataframe):

    dataframe_predict = dataframe.copy(deep=True)
    dataframe_predict['datemut'] = pd.to_datetime(dataframe_predict['datemut'],format="%Y-%m-%d")
    dataframe_predict['anneemut'] = dataframe_predict['datemut'].dt.year
    dataframe_predict['moismut'] = dataframe_predict['datemut'].dt.month
    dataframe_predict['jourmut'] = dataframe_predict['datemut'].dt.day
    dataframe_predict.drop(['Unnamed: 0', 'datemut','idmutinvar','idopendata','nbcomm','l_codinsee','coddep','l_idparmut','l_idpar','l_idlocmut','libtypbien','anneemut','geometry'], axis = 1, inplace = True)
    dataframe_predict = dataframe_predict.drop(dataframe_predict[dataframe_predict['valeurfonc'] <100].index)

    dataframe_viz = dataframe.copy(deep=True)
    dataframe_viz['datemut'] = pd.to_datetime(dataframe_viz['datemut'],format="%Y-%m-%d")
    dataframe_viz['anneemut'] = dataframe_viz['datemut'].dt.year
    dataframe_viz['moismut'] = dataframe_viz['datemut'].dt.month
    dataframe_viz['jourmut'] = dataframe_viz['datemut'].dt.day
    dataframe_viz.drop(['Unnamed: 0','idmutinvar','idopendata','nbcomm','l_codinsee','coddep','l_idparmut','l_idpar','l_idlocmut'], axis = 1, inplace = True)
    dataframe_viz = dataframe_viz[['datemut','anneemut','moismut','jourmut','libnatmut','vefa','nbparmut','sterr','sbati','nbvolmut','nblocmut','codtypbien','libtypbien','valeurfonc','geometry']]

    return dataframe_predict, dataframe_viz
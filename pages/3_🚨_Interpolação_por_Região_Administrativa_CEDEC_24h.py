import streamlit as st
import geopandas as gpd
from osgeo import gdal, ogr, osr
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from datetime import datetime, timedelta
import os
from rasterstats import zonal_stats
from dotenv import load_dotenv
import functions.geodados as geodados
import plotly.express as px


# Loading Environment Variables
load_dotenv()

st.set_page_config(layout="wide")
st.title('Interpolação IDW por Região Administrativa - Defesa Civil (CEDEC)')

st.sidebar.image('data/logo.png')

# Recebe o valor digitado no `st.text_input` como entrada do usuário
excluir_prefixos = st.text_input(
    "Digite os prefixos das estações a serem excluídas para remoção de outliers.",
    value="",  # valor inicial vazio
    placeholder="Exemplo: IAC-Ibitinga - SP, 350320801A",
    help="Digite os prefixos separados por vírgula. Consulte os prefixos no site do SIBH."
).strip()

# Processa a lista de prefixos inseridos, se houver algum
if excluir_prefixos:
    prefixos_para_excluir = [prefixo.strip() for prefixo in excluir_prefixos.split(",")]
    st.write(f"Prefixos a serem excluídos: {prefixos_para_excluir}")
else:
    st.write("Nenhum prefixo excluído.")

# Sliders para ajustar parâmetros da interpolação IDW
st.subheader("Parâmetros da Interpolação IDW")

power = st.slider(
    "Power (potência da interpolação)",
    min_value=0.0, max_value=5.0, value=2.0, step=0.1,
    help="A potência determina o peso da distância na interpolação."
)

smoothing = st.slider(
    "Smoothing (suavização)",
    min_value=0.0, max_value=1.0, value=0.1, step=0.01,
    help="A suavização reduz a variabilidade na interpolação. Valores maiores tornam o mapa mais suave e menos influenciado por variações locais. Maior generalização"
)

radius1 = st.slider(
    "Radius (raio de influência)",
    min_value=0.0, max_value=5.0, value=0.5, step=0.1,
    help="O raio determina a distância máxima em torno de cada ponto para considerar na interpolação. Valores maiores aumentam a área de influência. 10km de buffer corresponde a 0,1"
)


upload_to_geonode = st.checkbox("Salvar no Geodados?", value=False, help="Selecione caso queira salvar o resultado no Geodados \n(https://geodados.daee.sp.gov.br/#/)")

# Definição dos limites
bounds = [0, 1, 2, 5, 7, 10, 15, 20, 25, 30, 40, 50, 75, 100, 250]
bounds2 = [0, 5, 10, 15, 20, 30, 40, 50, 100, 125, 150, 200, 250, 300, 350]

# Dicionário de opções
options = {
    "Opção recomendada para períodos secos": bounds,
    "Opção recomendada para períodos chuvosos": bounds2,
}

# Interface do Streamlit para seleção do intervalo
selected_option = st.radio(
    "Selecione o intervalo de cores",
    list(options.keys()),  # Mostra as opções do dicionário
)

# Obter o intervalo selecionado com base na escolha
selected_bounds = options[selected_option]

# Exibir o intervalo selecionado
st.write("Intervalo selecionado:", str(selected_bounds))

def gerar_mapa_chuva(url, titulo, excluir_prefixos, date_time_id):
    # Carregando a fronteira do estado de São Paulo e criando um shapefile temporário
    cedec = gpd.read_file('./data/cedec2.shp', encoding='ISO-8859-1').to_crs(epsg=4326)
    minx, miny, maxx, maxy = cedec.total_bounds

    cedec_shapefile = "results/cedec.shp"
    cedec.to_file(cedec_shapefile)

    # Obtendo dados da API
    response = requests.get(url)
    data = response.json()

    # Extraindo coordenadas e valores
    stations = [
        (item["prefix"], float(item["latitude"]), float(item["longitude"]), item["value"])
        for item in data["json"]
        if item["latitude"] and item["longitude"] and item["value"]
    ]

    # Filtrando estações
    filtered_stations = [
        (lat, lon, value)
        for prefix, lat, lon, value in stations
        if prefix not in excluir_prefixos
    ]

    if not filtered_stations:
        st.error("Erro: Não há dados válidos para interpolação após a exclusão.")
        return

    # Separando latitudes, longitudes e valores
    lats, longs, values = zip(*filtered_stations)

    # Salvando os pontos em um shapefile temporário
    shapefile_path = "results/temp_points.shp"
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.CreateDataSource(shapefile_path)
    layer = dataSource.CreateLayer("layer", geom_type=ogr.wkbPoint)

    # Adicionando valores de precipitação
    layer.CreateField(ogr.FieldDefn("value", ogr.OFTReal))
    for lat, lon, value in zip(lats, longs, values):
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(lon, lat)
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(point)
        feature.SetField("value", value)
        layer.CreateFeature(feature)
        feature = None

    dataSource = None

    output_raster = f"results/cedec_idw_{date_time_id}.tif"
    gdal.Grid(
        output_raster,
        shapefile_path,
        zfield="value",
        algorithm=f"invdist:power={power}:smoothing={smoothing}:radius={radius1}",
        outputBounds=(minx, miny, maxx, maxy),
        width=1000, height=1000,
        #options=["noData=-9999"]  # Defina um noData explícito diferente de zero
    )

    if not os.path.exists(output_raster):
        st.error(f"Erro: O raster intermediário {output_raster} não foi criado.")
        return

    # Definindo sistema de coordenadas EPSG:4326 no raster
    raster = gdal.Open(output_raster, gdal.GA_Update)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    raster.SetProjection(srs.ExportToWkt())
    raster = None

    cropped_raster = f"results/cedec_idw_cropped_{date_time_id}.tif"
    gdal.Warp(
        cropped_raster,
        output_raster,
        cutlineDSName=cedec_shapefile,
        cropToCutline=True,
        dstNodata=np.nan,
    )

    # Zonal stats
    stats = zonal_stats(cedec, cropped_raster, stats=[estatistica_desejada], geojson_out=True)
    
    crs = {'init': 'epsg:4326'}
    cedec_stats = gpd.GeoDataFrame.from_features(stats, crs=crs)
    cedec_stats = cedec_stats.rename(columns={estatistica_desejada: f"{estatistica_desejada}_precipitation"})

    # Converte os dados de precipitação para tipo float, preenchendo NaNs com zero
    cedec_stats[f"{estatistica_desejada}_precipitation"] = pd.to_numeric(
        cedec_stats[f"{estatistica_desejada}_precipitation"], errors='coerce'
    ).fillna(0)

    cedec_stats_shp = cedec_stats.rename(columns={f"{estatistica_desejada}_precipitation": "rain"})
    cedec_stats_shp.to_file(f"./results/acumulado_24_mun_{ontem.strftime('%Y-%m-%d')}.shp", driver="ESRI Shapefile")


    # Make upload to Geodados
    if upload_to_geonode:
        geodados.make_upload_to_geonode(f"acumulado_24_mun_{str(ontem.strftime('%Y-%m-%d'))}", f"./results/acumulado_24_mun_{str(ontem.strftime('%Y-%m-%d'))}.shp", {
        "title": "Chuva Acumulada 24h - "+str(ontem.strftime('%Y-%m-%d')),
            "abstract": "Chuva acumulada das últimas 24h do dia "+str(ontem.strftime('%Y-%m-%d')),
            "category": 19,
            "license": 4, 
        }, "styles/rainfall_daily_polygon.sld")


    # Plot do resultado usando cedec_stats
    fig, ax = plt.subplots(figsize=(18, 12))

    cmap = ListedColormap([
        "#ffffff00", "#D5FFFF", "#00D5FF", "#0080AA", "#0000B3",
        "#80FF55", "#00CC7F", "#558000", "#005500", "#FFFF00",
        "#FFCC00", "#FF9900", "#D55500", "#FFBBFF", "#FF2B80", "#8000AA"
    ])


    norm = BoundaryNorm(selected_bounds, cmap.N)


    cedec_stats.plot(
        column=f"{estatistica_desejada}_precipitation",
        cmap=cmap,
        linewidth=0.3,
        edgecolor="black",
        legend=False,
        ax=ax,
        norm=norm
    )

    # Adicionar o colorbar manualmente
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="horizontal", label="Precipitação (mm)", shrink=0.75, pad=0.05, extend='max')
    cbar.set_ticks(selected_bounds)
    cbar.set_ticklabels([str(b) for b in selected_bounds])
    cedec.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.3)

    logo_path = "./data/logo.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        imagebox = OffsetImage(logo, zoom=0.2)
        ab = AnnotationBbox(
            imagebox,
            (0.91, 0.91),
            xycoords='axes fraction',
            frameon=True,
            bboxprops=dict(facecolor="white", edgecolor='none')
        )
        ax.add_artist(ab)

    annotation_text = (
        "Interpolação dos pluviômetros a partir do método IDW.\n"
        "Elaborado pela equipe técnica da Sala de Situação São Paulo (SSSP)."
    )
    ax.annotate(
        annotation_text, xy=(0.02, 0.02), xycoords='axes fraction',
        fontsize=8, ha='left', va='bottom',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='white')
    )

    ax.set_title(f'{titulo}', fontsize=14)
    ax.grid(which='both', linestyle='-', linewidth=0.5, color='gray', alpha=0.6)
    ax.tick_params(axis='both', which='major', labelsize=8)


    # Salvar a figura gerada
    mun_figure_path = f"./results/mun_figure_{hoje_format}.png"
    plt.savefig(mun_figure_path)    
    st.pyplot(fig)

    st.title("Sinópse automática")
    cedec_stats = cedec_stats.sort_values(by=f"{estatistica_desejada}_precipitation", ascending=False)
    maior_chuva_cedec = cedec_stats.iloc[0]["Nome"]
    maior_chuva_valor = cedec_stats.iloc[0][f"{estatistica_desejada}_precipitation"]
    maior_chuva_cedec2 = cedec_stats.iloc[1]["Nome"]
    maior_chuva_valor2 = cedec_stats.iloc[1][f"{estatistica_desejada}_precipitation"]
    maior_chuva_cedec3 = cedec_stats.iloc[2]["Nome"]
    maior_chuva_valor3 = cedec_stats.iloc[2][f"{estatistica_desejada}_precipitation"]
 

    if maior_chuva_valor < 3:
        st.write('O Estado de São Paulo não possui chuvas expressivas nas últimas 24 horas.')

    else:
        st.write(f"""
        A Região Administrativa com maior chuva no Estado de São Paulo, a partir da estatística "{estatistica_desejada}", foi **{maior_chuva_cedec}**, com um total de **{maior_chuva_valor:.2f} mm** de precipitação. Seguido de **{maior_chuva_cedec2}**, com um total de **{maior_chuva_valor2:.2f} mm**, e **{maior_chuva_cedec3}**, com um total de **{maior_chuva_valor3:.2f} mm**.
        """)

# Define the function for displaying table and interactive chart
def exibir_graficos_tabela(url, excluir_prefixos):
    cedec = gpd.read_file('./data/cedec2.shp', encoding='ISO-8859-1').to_crs(epsg=4326)
    minx, miny, maxx, maxy = cedec.total_bounds

    cedec_shapefile = "results/cedec2.shp"
    cedec.to_file(cedec_shapefile)

    # Obtendo dados da API
    response = requests.get(url)
    data = response.json()

    # Extraindo coordenadas e valores
    stations = [
        (item["prefix"], float(item["latitude"]), float(item["longitude"]), item["value"])
        for item in data["json"]
        if item["latitude"] and item["longitude"] and item["value"]
    ]

    # Filtrando estações
    filtered_stations = [
        (lat, lon, value)
        for prefix, lat, lon, value in stations
        if prefix not in excluir_prefixos
    ]

    if not filtered_stations:
        st.error("Erro: Não há dados válidos para interpolação após a exclusão.")
        return

    # Separando latitudes, longitudes e valores
    lats, longs, values = zip(*filtered_stations)

    # Salvando os pontos em um shapefile temporário
    shapefile_path = "results/temp_points.shp"
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.CreateDataSource(shapefile_path)
    layer = dataSource.CreateLayer("layer", geom_type=ogr.wkbPoint)

    # Adicionando valores de precipitação
    layer.CreateField(ogr.FieldDefn("value", ogr.OFTReal))
    for lat, lon, value in zip(lats, longs, values):
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(lon, lat)
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(point)
        feature.SetField("value", value)
        layer.CreateFeature(feature)
        feature = None

    dataSource = None

    output_raster = f"results/cedec_idw_{date_time_id}.tif"
    gdal.Grid(
        output_raster,
        shapefile_path,
        zfield="value",
        algorithm=f"invdist:power={power}:smoothing={smoothing}:radius={radius1}",
        outputBounds=(minx, miny, maxx, maxy),
        width=1000, height=1000,
    )

    if not os.path.exists(output_raster):
        st.error(f"Erro: O raster intermediário {output_raster} não foi criado.")
        return

    # Definindo sistema de coordenadas EPSG:4326 no raster
    raster = gdal.Open(output_raster, gdal.GA_Update)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    raster.SetProjection(srs.ExportToWkt())
    raster = None

    cropped_raster = f"results/cedec_idw_cropped_{date_time_id}.tif"
    gdal.Warp(
        cropped_raster,
        output_raster,
        cutlineDSName=cedec_shapefile,
        cropToCutline=True,
        dstNodata=np.nan,
    )

    # Zonal stats
    stats = zonal_stats(cedec, cropped_raster, stats=[estatistica_desejada], geojson_out=True)
    
    crs = {'init': 'epsg:4326'}
    cedec_stats = gpd.GeoDataFrame.from_features(stats, crs=crs)
    cedec_stats = cedec_stats.rename(columns={estatistica_desejada: f"{estatistica_desejada}_precipitation"})

    # Converte os dados de precipitação para tipo float, preenchendo NaNs com zero
    cedec_stats[f"{estatistica_desejada}_precipitation"] = pd.to_numeric(
        cedec_stats[f"{estatistica_desejada}_precipitation"], errors='coerce'
    ).fillna(0)

    cedec_stats = cedec_stats.rename(
        columns={
            "Nome": "Região Administrativa",
            f"{estatistica_desejada}_precipitation": "Precipitação (mm)"
        }
    )    
    cedec_stats = cedec_stats.sort_values(
        by="Precipitação (mm)",
        ascending=False  # Set to False for descending order
    )

    # Display the data table
    st.write("Tabela CEDEC")
    
    st.dataframe(
        cedec_stats[["Região Administrativa", "Precipitação (mm)"]], 
        hide_index=True
    )
    # Create and display an interactive bar chart
    st.write("Gráfico Estações")
    fig = px.bar(
        cedec_stats,
        x="Região Administrativa",
        y="Precipitação (mm)",
        labels={"Precipitação (mm)": "Precipitação (mm)"},
        title="Precipitação por Região Administrativa - CEDEC",
    )
    st.plotly_chart(fig)


# Entradas do usuário
hoje = datetime.now()
hoje_format = hoje.strftime('%Y-%m-%d')
ontem = hoje - timedelta(days=1)
ontem_format = ontem.strftime('%Y-%m-%d')

date_time_id = ontem.strftime("%Y%m%d%H%M")

url = f'https://cth.daee.sp.gov.br/sibh/api/v1/measurements/last_hours_events?hours=24&from_date={hoje_format}T07%3A00&show_all=true'
titulo = f"Acumulado de chuvas 24H\n07:00h de {ontem_format} às 07h de {hoje_format}"

opcoes_estatistica = ["max", "mean", "median", "majority"]
estatistica_desejada = st.selectbox(
    "Escolha a estatística para o cálculo de precipitação:", options=opcoes_estatistica,
    help="Selecione entre 'max', 'mean', 'median' ou 'majority'."
)
st.write(f"Estatística selecionada para cálculo de precipitação: **{estatistica_desejada}**")

# Chamar função com o botão
if st.button("Gerar Mapa"):
    gerar_mapa_chuva(url, titulo, excluir_prefixos, date_time_id)

if st.button("Gerar Tabela e Gráfico"):
    exibir_graficos_tabela(url, excluir_prefixos)


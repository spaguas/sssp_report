import streamlit as st
import geopandas as gpd
from osgeo import gdal, ogr, osr
import requests
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from datetime import datetime, timedelta, time
import os
import pandas as pd
from rasterstats import zonal_stats
from dotenv import load_dotenv
import functions.geodados as geodados
import plotly.express as px

load_dotenv()

def gerar_mapa_chuva(url, titulo, excluir_prefixos):
    # Carregando a fronteira do estado de São Paulo e criando um shapefile temporário
    sp_border = gpd.read_file('./data/DIV_MUN_SP_2021a.shp').to_crs(epsg=4326)
    minx, miny, maxx, maxy = sp_border.total_bounds

    sp_border_shapefile = "results/sp_border.shp"
    sp_border.to_file(sp_border_shapefile)

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

    output_raster = f"results/raster_idw_{date_time_id}.tif"
    gdal.Grid(
        output_raster,
        shapefile_path,
        zfield="value",
        algorithm=f"invdist:power={power}:smoothing={smoothing}:radius={radius}",
        outputBounds=(minx, miny, maxx, maxy),
        width=1000, height=1000,
    )

    if not os.path.exists(output_raster):
        st.error("Erro: O raster intermediário não foi criado.")
        return

    # Definindo sistema de coordenadas EPSG:4326 no raster
    raster = gdal.Open(output_raster, gdal.GA_Update)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    raster.SetProjection(srs.ExportToWkt())
    raster = None

    cropped_raster = f"results/raster_idw_cropped_{date_time_id}.tif"
    gdal.Warp(
        cropped_raster,
        output_raster,
        cutlineDSName=sp_border_shapefile,
        cropToCutline=True,
        dstNodata=np.nan,
    )

    if not os.path.exists(cropped_raster):
        st.error("Erro: O raster recortado não pôde ser criado.")
        return

    # Plot do resultado
    fig, ax = plt.subplots(figsize=(18, 12))

    # Carregar e plotar o raster recortado
    raster = gdal.Open(cropped_raster)
    if raster is None:
        st.error("Erro: O raster recortado não pôde ser aberto.")
        return

    raster_data = raster.ReadAsArray()

    cmap = ListedColormap([
        "#ffffff00", "#D5FFFF", "#00D5FF", "#0080AA", "#0000B3",
        "#80FF55", "#00CC7F", "#558000", "#005500", "#FFFF00",
        "#FFCC00", "#FF9900", "#D55500", "#FFBBFF", "#FF2B80", "#8000AA"
    ])

    norm = BoundaryNorm(selected_bounds, cmap.N)

    img = ax.imshow(raster_data, cmap=cmap, extent=(minx, maxx, miny, maxy), norm=norm)
    sp_border.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.3)

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

    cbar = fig.colorbar(img, ax=ax, orientation="horizontal", label="Precipitação (mm)", shrink=0.75, pad=0.05, extend='max')
    cbar.set_ticks(selected_bounds)
    cbar.set_ticklabels([str(b) for b in selected_bounds])
    cbar.ax.tick_params(labelsize=12)

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

    st.pyplot(fig)


def gerar_mapa_chuva_shapefile(url, titulo, excluir_prefixos, date_time_id, get_data, data_shapefile, arquivo, estatistica_desejada):
    # Carregando a fronteira do estado de São Paulo e criando um shapefile temporário
    minx, miny, maxx, maxy = get_data.total_bounds

    get_data.to_file(data_shapefile)

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

    output_raster = f"results/{arquivo}_{date_time_id}.tif"
    gdal.Grid(
        output_raster,
        shapefile_path,
        zfield="value",
        algorithm=f"invdist:power={power}:smoothing={smoothing}:radius={radius}",
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

    cropped_raster = f"results/{arquivo}_cropped_{date_time_id}.tif"
    
    gdal.Warp(
        cropped_raster,
        output_raster,
        cutlineDSName=data_shapefile,
        cropToCutline=True,
        dstNodata=np.nan,
    )

    # Zonal stats
    stats = zonal_stats(get_data, output_raster, stats=[estatistica_desejada], geojson_out=True)
    
    crs = {'init': 'epsg:4326'}
    data_stats = gpd.GeoDataFrame.from_features(stats, crs=crs)
    data_stats = data_stats.rename(columns={estatistica_desejada: f"{estatistica_desejada}_precipitation"})

    # Converte os dados de precipitação para tipo float, preenchendo NaNs com zero
    data_stats[f"{estatistica_desejada}_precipitation"] = pd.to_numeric(
        data_stats[f"{estatistica_desejada}_precipitation"], errors='coerce'
    ).fillna(0)
    
    data_stats_shp = data_stats.rename(columns={f"{estatistica_desejada}_precipitation": "rain"})
    data_stats_shp.to_file(f"./results/acumulado_24_mun_{data_hora_final.strftime('%Y-%m-%d')}.shp", driver="ESRI Shapefile")

    # Plot do resultado usando data_stats
    fig, ax = plt.subplots(figsize=(18, 12))

    cmap = ListedColormap([
        "#ffffff00", "#D5FFFF", "#00D5FF", "#0080AA", "#0000B3",
        "#80FF55", "#00CC7F", "#558000", "#005500", "#FFFF00",
        "#FFCC00", "#FF9900", "#D55500", "#FFBBFF", "#FF2B80", "#8000AA"
    ])

    norm = BoundaryNorm(selected_bounds, cmap.N)

    data_stats.plot(
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
    get_data.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.3)

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
        f"Interpolação dos pluviômetros a partir do método IDW. Parâmetros: Potência={power}, Suavização={smoothing} e Raio={radius}. "
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
    mun_figure_path = f"./results/mun_figure_{data_inicial_str}.png"
    plt.savefig(mun_figure_path)    
    st.pyplot(fig)

    st.title("Sinópse automática")

    if arquivo == 'cities_idw':
        data_stats = data_stats.sort_values(by=f"{estatistica_desejada}_precipitation", ascending=False)
        maior_chuva_municipio = data_stats.iloc[0]["NOME"]
        maior_chuva_valor = data_stats.iloc[0][f"{estatistica_desejada}_precipitation"]
        maior_chuva_municipio2 = data_stats.iloc[1]["NOME"]
        maior_chuva_valor2 = data_stats.iloc[1][f"{estatistica_desejada}_precipitation"]
        maior_chuva_municipio3 = data_stats.iloc[2]["NOME"]
        maior_chuva_valor3 = data_stats.iloc[2][f"{estatistica_desejada}_precipitation"]

        if maior_chuva_valor < 3:
            st.write('O Estado de São Paulo não possui chuvas expressivas nas últimas 24 horas do período selecionado.')
        else:
            st.write(f"""
            O município com maior chuva no Estado de São Paulo foi **{maior_chuva_municipio}**, com um total de **{maior_chuva_valor:.2f} mm** de precipitação. Seguido de **{maior_chuva_municipio2}**, com um total de **{maior_chuva_valor2:.2f} mm**, e **{maior_chuva_municipio3}**, com um total de **{maior_chuva_valor3:.2f} mm**.
            """)

        data_stats = data_stats.rename(
        columns={
            "NOME": "Município",
            f"{estatistica_desejada}_precipitation": "Precipitação (mm)"
        }
        )    
        data_stats = data_stats.sort_values(
            by="Precipitação (mm)",
            ascending=False  # Set to False for descending order
        )

        # Display the data table
        st.write("Tabela Municípios")
        st.dataframe(
            data_stats[["Município", "Precipitação (mm)"]], 
            hide_index=True
        )
        # Create and display an interactive bar chart
        st.write("Gráfico Estações")
        fig = px.bar(
            data_stats,
            x="Município",
            y="Precipitação (mm)",
            labels={"Precipitação (mm)": "Precipitação (mm)"},
            title="Precipitação por Municípios",
        )
        st.plotly_chart(fig)

        
    elif arquivo == "cedec_idw":
        data_stats = data_stats.sort_values(by=f"{estatistica_desejada}_precipitation", ascending=False)
        maior_chuva_cedec = data_stats.iloc[0]["Nome"]
        maior_chuva_valor = data_stats.iloc[0][f"{estatistica_desejada}_precipitation"]
        maior_chuva_cedec2 = data_stats.iloc[1]["Nome"]
        maior_chuva_valor2 = data_stats.iloc[1][f"{estatistica_desejada}_precipitation"]
        maior_chuva_cedec3 = data_stats.iloc[2]["Nome"]
        maior_chuva_valor3 = data_stats.iloc[2][f"{estatistica_desejada}_precipitation"]
        
        if maior_chuva_valor < 3:
            st.write('O Estado de São Paulo não possui chuvas expressivas nas últimas 24 horas.')
        else:
            st.write(f"""
            A Região Administrativa com maior chuva no Estado de São Paulo, a partir da estatística "{estatistica_desejada}", foi **{maior_chuva_cedec}**, com um total de **{maior_chuva_valor:.2f} mm** de precipitação. Seguido de **{maior_chuva_cedec2}**, com um total de **{maior_chuva_valor2:.2f} mm**, e **{maior_chuva_cedec3}**, com um total de **{maior_chuva_valor3:.2f} mm**.
            """)

        data_stats = data_stats.rename(
        columns={
            "Nome": "Região Administrativa",
            f"{estatistica_desejada}_precipitation": "Precipitação (mm)"
        }
        )    
        data_stats = data_stats.sort_values(
            by="Precipitação (mm)",
            ascending=False  # Set to False for descending order
        )

        # Display the data table
        st.write("Tabela CEDEC")
        
        st.dataframe(
            data_stats[["Região Administrativa", "Precipitação (mm)"]], 
            hide_index=True
        )
        # Create and display an interactive bar chart
        st.write("Gráfico Estações")
        fig = px.bar(
            data_stats,
            x="Região Administrativa",
            y="Precipitação (mm)",
            labels={"Precipitação (mm)": "Precipitação (mm)"},
            title="Precipitação por Região Administrativa - CEDEC",
        )
        st.plotly_chart(fig)

    elif arquivo == "ugrhi_idw":
        data_stats = data_stats.sort_values(by=f"{estatistica_desejada}_precipitation", ascending=False)
        data_stats = data_stats.rename(columns={"nome_ugrhi": "Ugrhi"})
        maior_chuva_cedec = data_stats.iloc[0]["Ugrhi"]
        maior_chuva_valor = data_stats.iloc[0][f"{estatistica_desejada}_precipitation"]
        maior_chuva_cedec2 = data_stats.iloc[1]["Ugrhi"]
        maior_chuva_valor2 = data_stats.iloc[1][f"{estatistica_desejada}_precipitation"]
        maior_chuva_cedec3 = data_stats.iloc[2]["Ugrhi"]
        maior_chuva_valor3 = data_stats.iloc[2][f"{estatistica_desejada}_precipitation"]
        
        if maior_chuva_valor < 3:
            st.write('O Estado de São Paulo não possui chuvas expressivas nas últimas 24 horas.')
        else:
            st.write(f"""
            A Ugrhi com maior chuva no Estado de São Paulo, a partir da estatística "{estatistica_desejada}", foi **{maior_chuva_cedec}**, com um total de **{maior_chuva_valor:.2f} mm** de precipitação. Seguido de **{maior_chuva_cedec2}**, com um total de **{maior_chuva_valor2:.2f} mm**, e **{maior_chuva_cedec3}**, com um total de **{maior_chuva_valor3:.2f} mm**.
            """)

        data_stats = data_stats.rename(
        columns={
            "Nome": "Unidade de gerenciamento de recursos hídricos (Ugri)",
            f"{estatistica_desejada}_precipitation": "Precipitação (mm)"
        }
        )    
        data_stats = data_stats.sort_values(
            by="Precipitação (mm)",
            ascending=False  # Set to False for descending order
        )

        # Display the data table
        st.write("Tabela de Unidade de gerenciamento de recursos hídricos (Ugri)")
        
        st.dataframe(
            data_stats[["Ugrhi", "Precipitação (mm)"]], 
            hide_index=True
        )
        # Create and display an interactive bar chart
        st.write("Gráfico de Unidade de gerenciamento de recursos hídricos (Ugri)")
        fig = px.bar(
            data_stats,
            x="Ugrhi",
            y="Precipitação (mm)",
            labels={"Precipitação (mm)": "Precipitação (mm)"},
            title="Precipitação por Ugrhi",
        )
        st.plotly_chart(fig)
    
    elif arquivo == "subugrhi_idw":
        data_stats = data_stats.sort_values(by=f"{estatistica_desejada}_precipitation", ascending=False)
        data_stats = data_stats.rename(columns={"no_subugrh": "Subugrhi"})
        maior_chuva_cedec = data_stats.iloc[0]["Subugrhi"]
        maior_chuva_valor = data_stats.iloc[0][f"{estatistica_desejada}_precipitation"]
        maior_chuva_cedec2 = data_stats.iloc[1]["Subugrhi"]
        maior_chuva_valor2 = data_stats.iloc[1][f"{estatistica_desejada}_precipitation"]
        maior_chuva_cedec3 = data_stats.iloc[2]["Subugrhi"]
        maior_chuva_valor3 = data_stats.iloc[2][f"{estatistica_desejada}_precipitation"]
        
        if maior_chuva_valor < 3:
            st.write('O Estado de São Paulo não possui chuvas expressivas nas últimas 24 horas.')
        else:
            st.write(f"""
            A Subugrhi com maior chuva no Estado de São Paulo, a partir da estatística "{estatistica_desejada}", foi **{maior_chuva_cedec}**, com um total de **{maior_chuva_valor:.2f} mm** de precipitação. Seguido de **{maior_chuva_cedec2}**, com um total de **{maior_chuva_valor2:.2f} mm**, e **{maior_chuva_cedec3}**, com um total de **{maior_chuva_valor3:.2f} mm**.
            """)

        data_stats = data_stats.rename(
        columns={
            "Nome": "Subugrhi",
            f"{estatistica_desejada}_precipitation": "Precipitação (mm)"
        }
        )    
        data_stats = data_stats.sort_values(
            by="Precipitação (mm)",
            ascending=False  # Set to False for descending order
        )

        # Display the data table
        st.write("Subugrhi")
        
        st.dataframe(
            data_stats[["Subugrhi", "Precipitação (mm)"]], 
            hide_index=True
        )
        # Create and display an interactive bar chart
        st.write("Gráfico de Unidade de gerenciamento de recursos hídricos (Ugri)")
        fig = px.bar(
            data_stats,
            x="Subugrhi",
            y="Precipitação (mm)",
            labels={"Precipitação (mm)": "Precipitação (mm)"},
            title="Precipitação por Ugrhi",
        )
        st.plotly_chart(fig)


def exibir_graficos_tabela_continuo(url, excluir_prefixos):
    # Fetching data from API
    response = requests.get(url)
    data = response.json()

    # Extracting station details and precipitation values
    stations = [
        (
            item.get("name"),
            item["prefix"],
            item.get("station_owner_name"), 
            item.get("city"),
            float(item["latitude"]),
            float(item["longitude"]),
            item["value"],
        )
        for item in data["json"]
        if item["latitude"] and item["longitude"] and item["value"]
    ]

    # Convert to DataFrame for easy display in Streamlit
    station_data_df = pd.DataFrame(
        stations,
        columns=['Nome', 'Prefixo', 'Proprietário', 'Município', 'Latitude', 'Longitude', 'Precipitação (mm)']
    )
    station_data_df = station_data_df.sort_values(by="Precipitação (mm)", ascending=False)

    
    # Filter stations based on excluded prefixes
    filtered_stations = [
        (name, prefix, owner, city, lat, lon, value)
        for name, prefix, owner, city, lat, lon, value in stations
        if prefix not in excluir_prefixos
    ]

    # Check for valid data after filtering
    if not filtered_stations:
        st.error("Erro: Não há dados válidos para exibição após a exclusão.")
        return

    # Display the data table
    st.write("Tabela Estações")
    st.dataframe(station_data_df,hide_index=True)  # Display data table in Streamlit

    # Create and display an interactive bar chart
    st.write("Gráfico Estações")
    fig = px.bar(
        station_data_df,
        x="Nome",
        y="Precipitação (mm)",
        labels={"Precipitação (mm)": "Precipitação (mm)", "Prefixo": "Nome"},
        title="Precipitação por Estações",
    )
    st.plotly_chart(fig)

# Parâmetros de entrada do usuário no Streamlit
st.title("Geração dos mapas interpolados dos pluviômetros")

st.write("""Esta ferramenta tem como objetivo realizar a interpolação da chuva das últimas 24h, dos pluviômetros, a partir do método IDW.\
            As estações podem ser consultadas no site do Sistema Integrado de Bacias Hidrográficas (https://cth.daee.sp.gov.br/sibh/chuva_agora).\
            Os resultados podem ser plotados de forma contínua ou agregados por município a partir de estatística escolhida (máxima, média, mediana ou moda)""")


option = st.selectbox(
    "Escolha o tipo de Interpolação:",
    ("Município", "Estação", "CEDEC", "Ugrhi", "Subugrhi"),
)

data_inicial = st.date_input("Escolha a data final:", value=datetime.today())
hora_inicial = st.time_input("Escolha a hora final:", value=time(7, 0))  # Hora padrão fixa para 07:00

# Combina a data e a hora selecionada em um único objeto datetime
data_hora_inicial = datetime.combine(data_inicial, hora_inicial)

# Formatação para construir a URL
data_inicial_str = data_hora_inicial.strftime('%Y-%m-%d')
hora_inicial_str = data_hora_inicial.strftime('%H:%M')

# Escolha do intervalo de horas
horas = st.number_input("Quantidade de horas retroativas para acumulação de chuva:", min_value=1, value=24)

data_hora_final = data_hora_inicial - timedelta(hours=horas)

# Exibe o datetime combinado para confirmar a seleção
st.write("Data e Hora Iniciais Selecionadas:", data_hora_final)
st.write("Data e Hora Finais Selecionadas:", data_hora_inicial)

date_time_id = data_hora_inicial.strftime("%Y%m%d%H%M")

# Sliders para ajustar parâmetros da interpolação IDW
st.subheader("Parâmetros da Interpolação IDW")

power = st.slider(
    "Power (potência da interpolação)",
    min_value=0.0, max_value=5.0, value=2.0, step=0.1,
    help="A potência determina o peso da distância na interpolação."
)

smoothing = st.slider(
    "Smoothing (suavização)",
    min_value=0.0, max_value=1.0, value=0.02, step=0.01,
    help="A suavização reduz a variabilidade na interpolação. Valores maiores tornam o mapa mais suave e menos influenciado por variações locais. Maior generalização"
)

radius = st.slider(
    "Radius em km (raio de influência)",
    min_value=0, max_value=500, value=50, step=1,
    help="O raio determina a distância máxima em torno de cada ponto para considerar na interpolação. Valores maiores aumentam a área de influência."
)
radius = radius/100



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

url = f'https://cth.daee.sp.gov.br/sibh/api/v1/measurements/last_hours_events?hours={horas}&from_date={data_inicial_str}T{hora_inicial_str}&show_all=true'
titulo = f"Acumulado de chuvas de {data_hora_final} à {data_hora_inicial}"

opcoes_estatistica = ["mean", "max", "median", "majority"]


estatistica_desejada = st.selectbox(
    "Escolha a estatística para o cálculo de precipitação:", options=opcoes_estatistica,
    help="Selecione entre 'max', 'mean', 'median' ou 'majority'."
)
st.write(f"Estatística selecionada para cálculo de precipitação: **{estatistica_desejada}**")



if option == "Estação":
    st.write('Interpolação por estações nas ultimas 24h')

    if st.button("Gerar Mapa e Gráficos"):
        gerar_mapa_chuva(url, titulo, excluir_prefixos)
        exibir_graficos_tabela_continuo(url, excluir_prefixos)


if option == "Município":
    st.write(f'Interpolação por município de {data_hora_final} à {data_hora_inicial}')

    sp_border = gpd.read_file('./data/DIV_MUN_SP_2021a.shp').to_crs(epsg=4326)
    sp_border_shapefile = "results/sp_border.shp"
    municipio_arquivo = 'cities_idw'

    # Chamar função com o botão
    if st.button("Gerar Mapa"):
        gerar_mapa_chuva_shapefile(url, titulo, excluir_prefixos, date_time_id, sp_border, sp_border_shapefile, municipio_arquivo, estatistica_desejada)


if option == "CEDEC":
    st.write(f'Interpolação por  Região Administrativa CEDEC de {data_hora_final} à {data_hora_inicial}')

    cedec = gpd.read_file('./data/cedec2.shp', encoding='ISO-8859-1').to_crs(epsg=4326)
    cedec_shapefile = "results/cedec.shp"
    cedec_arquivo = "cedec_idw"

    # Chamar função com o botão
    if st.button("Gerar Mapa"):
        gerar_mapa_chuva_shapefile(url, titulo, excluir_prefixos, date_time_id, cedec, cedec_shapefile, cedec_arquivo, estatistica_desejada)


if option == 'Ugrhi':
    st.write(f'Interpolação por Ugrhi de {data_hora_final} à {data_hora_inicial}')

    ugrhi = gpd.read_file('./data/ugrhi_sp_ipt_2009_gcs_wgs84.shp', encoding='UTF-8').to_crs(epsg=4326)
    ugrhi_shapefile = "results/ugrhi.shp"
    ugrhi_arquivo = "ugrhi_idw"

    # Chamar função com o botão
    if st.button("Gerar Mapa"):
        gerar_mapa_chuva_shapefile(url, titulo, excluir_prefixos, date_time_id, ugrhi, ugrhi_shapefile, ugrhi_arquivo, estatistica_desejada)

if option == 'Subugrhi':
    st.write(f'Interpolação por Subugrhi de {data_hora_final} à {data_hora_inicial}')

    ugrhi = gpd.read_file('./data/subugrhis_sp.shp', encoding='UTF-8').to_crs(epsg=4326)
    ugrhi_shapefile = "results/subugrhi.shp"
    ugrhi_arquivo = "subugrhi_idw"

    # Chamar função com o botão
    if st.button("Gerar Mapa"):
        gerar_mapa_chuva_shapefile(url, titulo, excluir_prefixos, date_time_id, ugrhi, ugrhi_shapefile, ugrhi_arquivo, estatistica_desejada)


if option == "Personalizado":
    st.write('Interpolação Personalizada')

    data_inicial = st.date_input("Escolha a data final:", value=datetime.today())
    hora_inicial = st.time_input("Escolha a hora final:", value=time(7, 0))  # Hora padrão fixa para 07:00

    # Combina a data e a hora selecionada em um único objeto datetime
    data_hora_inicial = datetime.combine(data_inicial, hora_inicial)

    # Exibe o datetime combinado para confirmar a seleção
    st.write("Data e Hora Finais Selecionadas:", data_hora_inicial)

    # Formatação para construir a URL
    data_inicial_str = data_hora_inicial.strftime('%Y-%m-%d')
    hora_inicial_str = data_hora_inicial.strftime('%H:%M')

    # Escolha do intervalo de horas
    horas = st.number_input("Quantidade de horas retroativas para acumulação de chuva:", min_value=1, value=24)

    data_hora_final = data_hora_inicial - timedelta(hours=horas)
    st.write("Data e Hora Iniciais Selecionadas:", data_hora_final)

    # Recebe o valor digitado no `st.text_input` como entrada do usuário
    excluir_prefixos = st.text_input(
        "Digite os prefixos das estações a serem excluídas para remoção de outliers.",
        value="",  # valor inicial vazio
        placeholder="Exemplo: IAC-Ibitinga - SP, 350320801A",
        help="Digite os prefixos separados por vírgula. Consulte os prefixos no site do SIBH."
    ).strip()

    # Construção da URL com os parâmetros
    url = f'https://cth.daee.sp.gov.br/sibh/api/v1/measurements/last_hours_events?hours={horas}&from_date={data_inicial_str}T{hora_inicial_str}&show_all=true'
    titulo = f"Acumulado de chuvas de {data_hora_final} à {data_hora_inicial}"

    date_time_id = data_hora_inicial.strftime("%Y%m%d%H%M")

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

    if st.button("Gerar Mapa"):
        gerar_mapa_chuva(url, titulo, excluir_prefixos)





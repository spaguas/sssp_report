import streamlit as st

import leafmap.foliumap as leafmap
from dotenv import load_dotenv

# Loading Environment Variables
load_dotenv()

st.set_page_config(layout="wide")
st.title('Geração dos mapas interpolados dos pluviômetros')

st.sidebar.image('data/logo.png')
st.title('Geração dos mapas interpolados dos pluviômetros')

st.write('Esta ferramenta tem como objetivo realizar a interpolação da chuva das últimas 24h, dos pluviômetros, a partir do método IDW.\
        As estações podem ser consultadas no site do Sistema Integrado de Bacias Hidrográficas (https://cth.daee.sp.gov.br/sibh/chuva_agora).\
         Os resultados podem ser plotados de forma contínua ou agregados por município a partir de estatística escolhida (máxima, média, mediana ou moda)...')


st.components.v1.iframe("https://cth.daee.sp.gov.br/sibh/chuva_agora", width=800, height=600)


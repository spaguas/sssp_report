import streamlit as st


st.title('Geração dos mapas interpolados dos pluviômetros')

st.sidebar.image('data/logo.png')

st.write('Esta ferramenta tem como objetivo realizar a interpolação da chuva das últimas 24h, dos pluviômetros, a partir do método IDW.\
        As estações podem ser consultadas no site do Sistema Integrado de Bacias Hidrográficas (https://cth.daee.sp.gov.br/sibh/chuva_agora).\
         Os resultados podem ser plotados de forma contínua ou agregados por município a partir de estatística escolhida (máxima, média, mediana ou moda)...')


st.components.v1.iframe("https://cth.daee.sp.gov.br/sibh/chuva_agora", width=1200, height=800)


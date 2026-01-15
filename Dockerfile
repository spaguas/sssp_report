FROM continuumio/miniconda3

WORKDIR /usr/src/app

# 1️⃣ Copia SOMENTE o environment.yml
COPY environment.yml .

# 2️⃣ Cria o ambiente (cacheável)
RUN conda env create -f environment.yml

# 3️⃣ Ativa o ambiente
ENV PATH=/opt/conda/envs/myenv/bin:$PATH

# 4️⃣ Agora copia o código
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

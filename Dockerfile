FROM continuumio/miniconda3

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN conda env create -f environment.yml

SHELL [ "conda","run","-n","myenv","/bin/bash","-c" ]

EXPOSE 8501

CMD ["conda", "run", "-n", "myenv", "streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
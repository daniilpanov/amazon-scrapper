FROM python:3.10-slim AS capsolver

WORKDIR '/src'

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt
EXPOSE 8090
ENTRYPOINT ["python3", "app/serve.py"]

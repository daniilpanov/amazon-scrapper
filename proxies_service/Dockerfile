FROM python:3.11-slim AS proxies_manager

WORKDIR '/src'

COPY ./requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8833
ENTRYPOINT ["python3", "app/serve.py"]

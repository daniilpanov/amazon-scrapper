FROM python:3.11-slim AS proxies_manager

WORKDIR '/app'

COPY ./ ./

RUN pip3 install -r requirements.txt
EXPOSE 8833
ENTRYPOINT ["python3", "app/serve.py"]

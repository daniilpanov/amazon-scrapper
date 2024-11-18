FROM python:3.11-slim AS dataimporter

WORKDIR '/app'

COPY ./ ./

RUN pip3 install -r requirements.txt
EXPOSE 8831
ENTRYPOINT ["python3", "app/serve.py"]

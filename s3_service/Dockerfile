FROM python:3.11-slim AS s3

WORKDIR '/app'

COPY ./ ./

RUN pip3 install -r requirements.txt
EXPOSE 8836
ENTRYPOINT ["python3", "app/serve.py"]

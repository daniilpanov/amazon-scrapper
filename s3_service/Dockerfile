FROM python:3.11-slim AS s3

WORKDIR '/src'

COPY ./requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8836
ENTRYPOINT ["python3", "app/serve.py"]

FROM python:3.11-slim AS google_upload

WORKDIR '/app'

COPY ./ ./

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "app/serve.py"]

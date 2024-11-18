FROM python:3.11-slim AS web

WORKDIR '/app'

COPY ./ ./

RUN pip3 install -r requirements.txt
EXPOSE 8838
ENTRYPOINT ["python3", "app/serve.py"]

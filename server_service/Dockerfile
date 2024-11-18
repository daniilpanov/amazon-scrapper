FROM python:3.11-slim AS server

WORKDIR '/app'

COPY ./ ./

RUN pip3 install -r requirements.txt
EXPOSE 8832
ENTRYPOINT ["gunicorn", "--workers", "2", "--preload", "--worker-class=uvicorn.workers.UvicornWorker", "app:app"]

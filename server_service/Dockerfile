FROM python:3.11-slim AS server

WORKDIR '/app'

COPY ./ ./

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn
EXPOSE 8832
ENTRYPOINT ["gunicorn", "app:app"]
CMD ["--workers", "2", "--preload", "--worker-class=uvicorn.workers.UvicornWorker", "--host", "0.0.0.0", "--port", "8832"]

FROM python:3.11-slim AS server

WORKDIR '/app'

COPY ./ ./

RUN pip3 install -r requirements.txt
EXPOSE 8832
ENTRYPOINT ["python3", "app/serve.py"]

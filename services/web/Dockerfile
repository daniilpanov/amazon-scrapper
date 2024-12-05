FROM python:3.11-slim AS web

WORKDIR '/src'

COPY requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
ENTRYPOINT ["uvicorn", "app:app"]

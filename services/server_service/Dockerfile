FROM python:3.11-slim AS server

WORKDIR '/src'

COPY requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install gunicorn
ENTRYPOINT ["gunicorn", "app:app"]

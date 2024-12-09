FROM python:3.11-slim AS loader

WORKDIR '/src'

COPY requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir gunicorn
ENTRYPOINT ["gunicorn", "app:app"]

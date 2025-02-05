FROM python:3.10-slim AS capsolver

WORKDIR '/src'

COPY requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python3", "app/serve.py"]

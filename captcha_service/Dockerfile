FROM python:3.11-slim AS capsolver

WORKDIR '/app'

COPY ./ ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app/serve.py"]

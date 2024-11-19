FROM python:3.11-slim AS web

WORKDIR '/src'

COPY ./ ./

RUN pip3 install -r requirements.txt
EXPOSE 8838
ENTRYPOINT ["uvicorn", "app:app"]
CMD ["--host", "0.0.0.0", "--port", "8838"]

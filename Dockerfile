FROM python:3.11-slim as bsrstarter

WORKDIR '/usr/src/bsrstarter'

COPY ./bsr_starter_service/ ./

ENTRYPOINT ["top", "-b"]
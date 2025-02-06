FROM python:3.11-alpine

WORKDIR '/src'

RUN apk add --no-cache bash dcron logrotate curl tini

COPY requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["tini", "--"]
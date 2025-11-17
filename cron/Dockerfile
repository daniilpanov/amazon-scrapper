FROM alpine:latest

WORKDIR "/src"

RUN apk add --no-cache bash dcron logrotate curl tini

ENTRYPOINT ["tini", "--"]
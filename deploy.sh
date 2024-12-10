#!/usr/bin/env bash
docker image rm danielgreen1806/amascrap-simple_server:latest danielgreen1806/amascrap-light:latest danielgreen1806/amascrap-google:latest danielgreen1806/amascrap-s3:latest

docker build ./dockerfiles/simple_server -t danielgreen1806/amascrap-simple_server:latest
docker build ./dockerfiles/light -t danielgreen1806/amascrap-light:latest
docker build ./dockerfiles/google -t danielgreen1806/amascrap-google:latest
docker build ./dockerfiles/s3 -t danielgreen1806/amascrap-s3:latest

# docker push danielgreen1806/amascrap-simple_server
# docker push danielgreen1806/amascrap-light
# docker push danielgreen1806/amascrap-google
# docker push danielgreen1806/amascrap-s3

docker compose up --no-build $@
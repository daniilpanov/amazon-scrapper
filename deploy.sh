#!/usr/bin/env bash
docker build ./dockerfiles/simple_server -t danielgreen1806/amascrap-simple_server
docker build ./dockerfiles/light -t danielgreen1806/amascrap-light
docker build ./dockerfiles/google -t danielgreen1806/amascrap-google
docker build ./dockerfiles/s3 -t danielgreen1806/amascrap-s3

# docker push danielgreen1806/amascrap-simple_server
# docker push danielgreen1806/amascrap-light
# docker push danielgreen1806/amascrap-google
# docker push danielgreen1806/amascrap-s3

docker compose up --no-build $@
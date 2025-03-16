FROM python:3.11-slim

WORKDIR '/src'

RUN apt-get -y update; apt-get install -y ffmpeg libsm6 libxext6

COPY requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

FROM python:3.11 AS s3_upload

WORKDIR '/src'

COPY ./requirements.txt ./requirements.txt

RUN apt-get -y update
#RUN apt-get install -y software-properties-common \
#RUN add-apt-repository -y ppa:jonathonf/ffmpeg-4
#RUN apt-get update
#RUN apt-get install -y ffmpeg
RUN apt-get install -y ffmpeg libsm6 libxext6

RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "app/serve.py"]

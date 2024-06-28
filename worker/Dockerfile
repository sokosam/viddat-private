FROM python:3.11-bullseye

WORKDIR /worker

COPY . /worker/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ffmpeg 

RUN pip install --no-cache-dir -r requirements.txt

COPY fonts/ /usr/share/fonts/

RUN fc-cache -f -v


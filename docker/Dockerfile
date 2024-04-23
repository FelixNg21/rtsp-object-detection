# syntax=docker/dockerfile:1

FROM python:3.10.14 as base
WORKDIR /app
COPY requirements.txt /app

FROM base as final

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update && \
   apt-get -y install libgl1-mesa-glx

COPY . /app

CMD ["python", "cam_detect_yolo_docker.py"]




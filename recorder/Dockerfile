# syntax=docker/dockerfile:1

FROM python:3.10.14 AS base
WORKDIR /app
COPY requirements.txt /app
ENV PYTHONUNBUFFERED=1
FROM base AS final

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update && \
   apt-get -y install libgl1-mesa-glx libglib2.0-0 libxkbcommon-x11-0 libxcb-xinerama0
RUN pip uninstall -y opencv-python
RUN pip install opencv-python-headless

COPY . /app

CMD ["python", "runner.py"]



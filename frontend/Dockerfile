FROM python:3.10.14 as base
WORKDIR /app
COPY requirements.txt /app

FROM base as final

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "frontend-flask", "run", "--host=0.0.0.0"]
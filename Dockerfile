FROM python3.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY requirements.txt /code/

COPY vendor /code/vendor/

RUN pip3 install -r requirements.txt

WORKDIR /code

COPY . /code/

WORKDIR /code/backend

EXPOSE 8000

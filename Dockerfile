FROM python:3.10-alpine3.20

ENV PYTHONUNBUFFERED 1

WORKDIR /telegram_app

ENV PYTHONPATH=${PYTHONPATH}:/telegram_app/management/commands

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
FROM python:3.12-alpine3.20
LABEL maintaner="toys4babyodua@gmail.com"

ENV PYTHOUNNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY .. .

RUN adduser \
    --disabled-password \
    --nocreate-home \
    my_user \

USER my_user

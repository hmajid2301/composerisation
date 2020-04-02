FROM python:alpine3.7
LABEL MAINTAINER="Haseeb Majid me@haseebmajid.dev"
LABEL VERSION="0.1.0-beta.4"

COPY dist ./dist/
RUN pip install dist/*
WORKDIR /app

ENTRYPOINT [ "composerisation", "-i", "/app/docker-compose.yml" ]

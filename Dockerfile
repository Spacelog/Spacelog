# syntax = docker/dockerfile:1.2
FROM ubuntu:16.04
RUN apt-get update -qq && apt-get install -yq imagemagick optipng procps python python-pip python-xapian  
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /src
WORKDIR /src
COPY requirements.txt /src/
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY . /src/
# TODO: depends on redis...
# RUN make productioncss && make collectstatic

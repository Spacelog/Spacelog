# syntax = docker/dockerfile:1.2
FROM golang AS overmind-builder

RUN go install github.com/DarthSim/overmind/v2@latest

FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -yq \
        bash \
        tmux \
        curl

COPY --from=overmind-builder /go/bin/overmind /usr/bin/
CMD ["overmind", "start"]

RUN apt-get update -qq && apt-get install -yq imagemagick optipng procps python python-pip python-xapian redis-server
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /src

WORKDIR /src
COPY requirements.txt /src/
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY . /src/
RUN /etc/init.d/redis-server start && \
  make all

# syntax = docker/dockerfile:1.2
FROM golang:1.20.4 AS overmind-builder

RUN go install github.com/DarthSim/overmind/v2@latest

FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -yq \
        bash \
        tmux \
        curl

COPY --from=overmind-builder /go/bin/overmind /usr/bin/
CMD ["overmind", "start"]

RUN apt-get update -qq && \
    apt-get install -yq \
        imagemagick optipng procps \
        python python-pip python-xapian \
        redis-server \
        nginx
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /src

WORKDIR /src
COPY requirements.txt /src/
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY . /src/
RUN /etc/init.d/redis-server start && \
  make all && \
  redis-cli shutdown save

EXPOSE 8000
EXPOSE 8001
EXPOSE 9000

ENV GLOBAL_PORT 8000
ENV WEBSITE_PORT 8001
ENV NGINX_PORT 9000

# In production mode, generate links that point to port-less URLs
ENV GLOBAL_LINK_PORT 80
ENV WEBSITE_LINK_PORT 80

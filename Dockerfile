FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmagic1 \
        locales && \
    locale-gen en_GB.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN mkdir /home/messytables && \
    chown nobody /home/messytables
USER nobody
ENV HOME=/home/messytables \
    PATH=/home/messytables/.local/bin:$PATH \
    LANG=en_GB.UTF-8
WORKDIR /home/messytables

COPY --chown=nobody pyproject.toml uv.lock /home/messytables/
RUN uv sync
COPY --chown=nobody . /home/messytables/

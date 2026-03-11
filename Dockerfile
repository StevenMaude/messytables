FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmagic1 \
        locales && \
    locale-gen en_GB.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=en_GB.UTF-8

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN useradd -m -d /home/messytables messytables
USER messytables
ENV HOME=/home/messytables \
    PATH=/home/messytables/.local/bin:$PATH
WORKDIR /home/messytables

COPY --chown=messytables pyproject.toml uv.lock ./
RUN uv sync --extra dev --frozen

COPY --chown=messytables . .

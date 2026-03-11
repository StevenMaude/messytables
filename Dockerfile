FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_GB.UTF-8 \
    LC_ALL=en_GB.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmagic1 \
        locales && \
    locale-gen en_GB.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . /app/
RUN uv sync --all-extras

ENTRYPOINT ["uv", "run", "pytest"]

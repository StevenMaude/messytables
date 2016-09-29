FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        python-pip \
        python3-pip

RUN locale-gen en_GB.UTF-8

RUN mkdir /home/messytables && \
    chown nobody /home/messytables
USER nobody
ENV HOME=/home/messytables \
    PATH=/home/messytables/.local/bin:$PATH \
    LANG=en_GB.UTF-8
# LANG needed for httpretty install on Py3
WORKDIR /home/messytables

COPY ./requirements-test.txt /home/messytables/
RUN pip install --user -r /home/messytables/requirements-test.txt
RUN pip3 install --user -r /home/messytables/requirements-test.txt
RUN pip install --user pdftables
COPY . /home/messytables/

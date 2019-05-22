FROM python:3.6-alpine

LABEL maintainer="https://github.com/AlexCPU/VictronVenus-InfluxDB"

ENV INFLUXDB=localhost
ENV INFLUXPORT=8086
ENV VENUS=192.168.1.2
ENV VENUSPORT=502
ENV UNITID=100

ADD requirements.txt /

RUN apk add --no-cache --update alpine-sdk && \
    pip3 install -r /requirements.txt && \
    apk del alpine-sdk

ADD venus.py /

CMD python3 /venus.py --influxdb $INFLUXDB --influxport $INFLUXPORT --port $VENUSPORT --unitid $UNITID $VENUS

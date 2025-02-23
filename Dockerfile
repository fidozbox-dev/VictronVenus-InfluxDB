# Use a more recent Python version for better security and features
FROM python:3.11-alpine

LABEL maintainer="https://github.com/fidozbox-dev/VictronVenus-InfluxDB"

# Group ENV statements for better readability
ENV INFLUXDB=localhost \
    INFLUXPORT=8086 \
    VENUS=192.168.1.2 \
    VENUSPORT=502 \
    UNITID=100

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Combine RUN commands and clean up in the same layer
RUN apk add --no-cache --update alpine-sdk && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del alpine-sdk

# Copy application code
COPY venus.py .

CMD ["python3", "./venus.py", "--influxdb", "$INFLUXDB", "--influxport", "$INFLUXPORT", "--port", "$VENUSPORT", "--unitid", "$UNITID", "$VENUS"]

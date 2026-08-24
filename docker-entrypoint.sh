#!/bin/sh
set -e

# Map the documented environment variables onto venus.py's CLI arguments.
# The Venus IP is a positional argument, so it goes last.
exec python venus.py \
    --influxdb   "${INFLUXDB:-localhost}" \
    --influxport "${INFLUXPORT:-8086}" \
    --port       "${VENUSPORT:-502}" \
    --unitid     "${UNITID:-100}" \
    ${DEBUG:+-d} \
    "${VENUS:-192.168.10.112}"

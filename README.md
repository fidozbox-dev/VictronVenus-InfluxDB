Victron Venus InfluxDB monitor
==========================

This is a simple python tool to export Victron Venus data to
an InfluxDb <https://www.influxdata.com/time-series-platform/influxdb/> for monitoring purposes. 
Docker Usage
---
```
docker run -d \ 
    -e INFLUXDB=<hostname/IP of InfluxDB server - default=localhost> \ 
    -e INFLUXPORT=<port InfluxDB is running on - default=8086> \ 
    -e VENUS=<hostname/IP of Venus Device - default=192.168.1.2> \
    -e VENUSPORT=<ModbusTCP port on Venus device - default=502> \
    -e UNITID=<Modbus ID of Venus Device - default=100> \
    alexcpu/VictronVenus-InfluxDB
```
Please replace user variables in the above command defined by <> with the correct values.  Environment variables can be excluded if the defaults are suitable.

Docker Example
---
```
docker run -d \ 
    -e INFLUXDB=192.168.1.50 \ 
    -e VENUS=192.168.1.200 \
    alexcpu/VictronVenus-InfluxDB
```

Command Line Usage:
------
`./venus.py [inverter IP]`

In addition, you can specify additional flags to customize the tool:
* `--influxdb` specifies the IP or hostname of the InfluxDb (default localhost)
* `--influxport` specifies the port InfluxDb is running on (default 8086)
* `--unitid` specifies the ModBus ID used by the inverter (default 100)
* `--port` specifies the ModBus TCP port to connect to (default 502)
* `-d` or `--debug` activates debug logging

# Victron Venus InfluxDB Monitor

A Python tool to export Victron Venus data to InfluxDB for monitoring purposes.

## Features
- ModbusTCP communication with Victron Venus devices
- Automatic data collection and storage in InfluxDB
- Docker support for easy deployment
- Configurable logging and debugging

## Requirements
- Python 3.6+
- InfluxDB instance
- Victron Venus device accessible via network

## Docker Usage

### Quick Start
```bash
docker run -d \
    -e INFLUXDB=<influxdb-host> \
    -e VENUS=<venus-host> \
    fidozbox/victronvenus-influxdb

docker run -d \ 
    -e INFLUXDB=<hostname/IP of InfluxDB server - default=localhost> \ 
    -e INFLUXPORT=<port InfluxDB is running on - default=8086> \ 
    -e VENUS=<hostname/IP of Venus Device - default=192.168.1.2> \
    -e VENUSPORT=<ModbusTCP port on Venus device - default=502> \
    -e UNITID=<Modbus ID of Venus Device - default=100> \
    fidozbox/VictronVenus-InfluxDB
Please replace user variables in the above command defined by <> with the correct values. Environment variables can be excluded if the defaults are suitable.


```

### Available Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| INFLUXDB | InfluxDB host | localhost |
| INFLUXPORT | InfluxDB port | 8086 |
| VENUS | Venus device host | 192.168.1.2 |
| VENUSPORT | ModbusTCP port | 502 |
| UNITID | Modbus unit ID | 100 |

## Local Installation

1. Clone the repository:
```bash
git clone https://github.com/fidozbox-dev/VictronVenus-InfluxDB.git
cd VictronVenus-InfluxDB
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the script:
```bash
python venus.py [venus-ip] [options]
```

### Command Line Options
| Option | Description | Default |
|--------|-------------|---------|
| --influxdb | InfluxDB host | localhost |
| --influxport | InfluxDB port | 8086 |
| --port | ModbusTCP port | 502 |
| --unitid | Modbus unit ID | 100 |
| -d, --debug | Enable debug logging | - |

## Support
For issues and feature requests, please use the [GitHub issue tracker](https://github.com/fidozbox-dev/VictronVenus-InfluxDB/issues).
```

Improvements from Original AlexCPU repo:
1. Update dependencies with specific versions
2. Modernize the Dockerfile with best practices
3. Make the README more comprehensive and professional
4. Add better documentation structure
5. Use Docker multi-stage build for smaller image size

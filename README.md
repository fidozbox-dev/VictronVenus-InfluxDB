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


```
## data structure notes :

    # reg_block[0] = Serial
    # reg_block[1] = Serial
    # reg_block[2] = Serial
    # reg_block[3] = Serial
    # reg_block[4] = Serial
    # reg_block[5] = Serial
    # reg_block[6] = CCGX Relay 1 State
    # reg_block[7] = CCGX Relay 2 State
    # reg_block[8] = PV - AC-coupled on output L1
    # reg_block[9] = PV - AC-coupled on output L2
    # reg_block[10] = PV - AC-coupled on output L3
    # reg_block[11] = PV - AC-coupled on input L1
    # reg_block[12] = PV - AC-coupled on input L2
    # reg_block[13] = PV - AC-coupled on input L3
    # reg_block[14] = PV - AC-coupled on generator L1
    # reg_block[15] = PV - AC-coupled on generator L2
    # reg_block[16] = PV - AC-coupled on generator L3
    # reg_block[17] = AC Consumption L1
    # reg_block[18] = AC Consumption L2
    # reg_block[19] = AC Consumption L3
    # reg_block[20] = Grid L1
    # reg_block[21] = Grid L2
    # reg_block[22] = Grid L3
    # reg_block[23] = Genset L1
    # reg_block[24] = Genset L2
    # reg_block[25] = Genset L3
    # reg_block[26] = Active input source
    
    # reg_block[0] = Battery Voltage (System)
    # reg_block[1] = Battery Current (System)
    # reg_block[2] = Battery Power (System)
    # reg_block[3] = Battery State of Charge (System)
    # reg_block[4] = Battery state (System)
    # reg_block[5] = Battery Consumed Amphours (System)
    # reg_block[6] = Battery Time to Go (System)

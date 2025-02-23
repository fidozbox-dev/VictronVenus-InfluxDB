#!/usr/bin/env python3
"""
Victron Venus to InfluxDB Bridge
Collects data from Victron Venus device via ModbusTCP and stores it in InfluxDB.
"""

import argparse
import datetime
import logging
from typing import Dict, Optional
import asyncio
import numpy as np
from aiohttp import ClientConnectionError
from pyModbusTCP.client import ModbusClient
from aioinflux import InfluxDBClient, InfluxDBWriteError

# Constants for Modbus registers
MODBUS_REGISTERS = {
    'SYSTEM_INFO': {'start': 800, 'count': 27},
    'BATTERY_INFO': {'start': 840, 'count': 7}
}

# Constants for scaling factors
SCALE_FACTORS = {
    'battery_voltage': 0.1,
    'battery_current': 0.1,
    'battery_power': 1,
    'battery_soc': 1,
    'battery_state': 1,
    'battery_ttg': 1,
    'ac_consumption': 1,
    'grid': 1,
    'pv_input': 1,
    'pv_output': 1,
    'active_input': 1
}

class VictronMonitor:
    """Main class for handling Victron Venus monitoring"""
    
    def __init__(self, venus_host: str, modbus_port: int, unit_id: int):
        """Initialize VictronMonitor with connection parameters"""
        self.logger = logging.getLogger('victron')
        self.client = ModbusClient(
            host=venus_host,
            port=modbus_port,
            unit_id=unit_id,
            auto_open=True,
            debug=True
        )

    async def read_modbus_registers(self, start: int, count: int) -> Optional[list]:
        """Read Modbus registers with error handling"""
        try:
            reg_block = self.client.read_holding_registers(start, count)
            if not reg_block:
                self._handle_modbus_error()
            return reg_block
        except Exception as e:
            self.logger.error(f'Error reading Modbus registers: {e}')
            return None

    def _handle_modbus_error(self):
        """Handle Modbus communication errors"""
        error_code = self.client.last_error()
        if error_code == 2:
            self.logger.error(f'Failed to connect to Victron Host {self.client.host()}!')
        elif error_code in (3, 4):
            self.logger.error('Send or receive error!')
        elif error_code == 5:
            self.logger.error('Timeout during send or receive operation!')

    def process_system_data(self, reg_block: list) -> Dict:
        """Process system-related register data"""
        return {
            'AC Consumption L1': reg_block[17] * SCALE_FACTORS['ac_consumption'],
            'AC Consumption L2': reg_block[18] * SCALE_FACTORS['ac_consumption'],
            'AC Consumption L3': reg_block[19] * SCALE_FACTORS['ac_consumption'],
            'Grid L1': np.int16(reg_block[20]) * SCALE_FACTORS['grid'],
            'Grid L2': np.int16(reg_block[21]) * SCALE_FACTORS['grid'],
            'Grid L3': np.int16(reg_block[22]) * SCALE_FACTORS['grid'],
            'PV - AC-coupled on input L1': reg_block[11] * SCALE_FACTORS['pv_input'],
            'PV - AC-coupled on input L2': reg_block[12] * SCALE_FACTORS['pv_input'],
            'PV - AC-coupled on input L3': reg_block[13] * SCALE_FACTORS['pv_input'],
            'PV - AC-coupled on output L1': reg_block[8] * SCALE_FACTORS['pv_output'],
            'PV - AC-coupled on output L2': reg_block[9] * SCALE_FACTORS['pv_output'],
            'PV - AC-coupled on output L3': reg_block[10] * SCALE_FACTORS['pv_output'],
            'Active input source': reg_block[26] * SCALE_FACTORS['active_input']
        }

    def process_battery_data(self, reg_block: list) -> Dict:
        """Process battery-related register data"""
        return {
            'Battery Voltage': reg_block[0] * SCALE_FACTORS['battery_voltage'],
            'Battery Current': np.int16(reg_block[1]) * SCALE_FACTORS['battery_current'],
            'Battery Power': np.int16(reg_block[2]) * SCALE_FACTORS['battery_power'],
            'Battery State of Charge': reg_block[3] * SCALE_FACTORS['battery_soc'],
            'Battery State': reg_block[4] * SCALE_FACTORS['battery_state'],
            'Battery Time to Go': reg_block[6] * SCALE_FACTORS['battery_ttg']
        }

    @staticmethod
    def create_datapoint(fields: Dict) -> Dict:
        """Create an InfluxDB datapoint with the current timestamp"""
        return {
            'measurement': 'Victron',
            'tags': {'system': 1},
            'fields': {k: float('%.2f' % v) for k, v in fields.items()},
            'time': datetime.datetime.utcnow().replace(
                tzinfo=datetime.timezone.utc
            ).isoformat()
        }

class InfluxDBWriter:
    """Handles InfluxDB connections and writes"""
    
    def __init__(self, host: str, port: int, database: str = 'victron'):
        self.host = host
        self.port = port
        self.database = database
        self.logger = logging.getLogger('victron')

    async def initialize(self) -> Optional[InfluxDBClient]:
        """Initialize InfluxDB connection"""
        try:
            client = InfluxDBClient(
                host=self.host,
                port=self.port,
                db=self.database
            )
            await client.create_database(db=self.database)
            self.logger.info('Database opened and initialized')
            return client
        except ClientConnectionError as e:
            self.logger.error(f'Error during connection to InfluxDB {self.host}: {e}')
            return None

async def main_loop(victron: VictronMonitor, influx_writer: InfluxDBWriter):
    """Main monitoring loop"""
    influx_client = await influx_writer.initialize()
    if not influx_client:
        return

    while True:
        try:
            # Read and process system data
            if system_regs := await victron.read_modbus_registers(
                MODBUS_REGISTERS['SYSTEM_INFO']['start'],
                MODBUS_REGISTERS['SYSTEM_INFO']['count']
            ):
                system_data = victron.process_system_data(system_regs)
                await influx_client.write(victron.create_datapoint(system_data))

            # Read and process battery data
            if battery_regs := await victron.read_modbus_registers(
                MODBUS_REGISTERS['BATTERY_INFO']['start'],
                MODBUS_REGISTERS['BATTERY_INFO']['count']
            ):
                battery_data = victron.process_battery_data(battery_regs)
                await influx_client.write(victron.create_datapoint(battery_data))

        except InfluxDBWriteError as e:
            victron.logger.error(f'Failed to write to InfluxDB: {e}')
        except Exception as e:
            victron.logger.error(f'Unhandled exception: {e}')

        await asyncio.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Victron Venus monitoring tool')
    parser.add_argument('--influxdb', default='localhost', help='InfluxDB host')
    parser.add_argument('--influxport', type=int, default=8086, help='InfluxDB port')
    parser.add_argument('--port', type=int, default=502, help='ModBus TCP port')
    parser.add_argument('--unitid', type=int, default=100, help='ModBus unit ID')
    parser.add_argument('venus', metavar='Venus-IP', help='Venus device IP address')
    parser.add_argument('--debug', '-d', action='count', help='Enable debug logging')
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig()
    if args.debug and args.debug >= 1:
        logging.getLogger('victron').setLevel(logging.DEBUG)
    if args.debug and args.debug == 2:
        logging.getLogger('aioinflux').setLevel(logging.DEBUG)

    print('Starting Victron Venus monitoring')
    print(f'Connecting to Victron Venus {args.venus} on port {args.port} using unit ID {args.unitid}')
    print(f'Writing data to InfluxDB {args.influxdb} on port {args.influxport}')

    # Initialize components and start monitoring
    victron_monitor = VictronMonitor(args.venus, args.port, args.unitid)
    influx_writer = InfluxDBWriter(args.influxdb, args.influxport)
    
    asyncio.get_event_loop().run_until_complete(
        main_loop(victron_monitor, influx_writer)
    )

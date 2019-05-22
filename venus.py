#!/usr/bin/env python3
import argparse
import datetime
import logging
import numpy as np

from aiohttp import ClientConnectionError
from pyModbusTCP.client import ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import asyncio
from aioinflux import InfluxDBClient, InfluxDBWriteError

datapoint = {
    'measurement': 'Victron',
    'tags': {},
    'fields': {}
}
reg_block = {}
logger = logging.getLogger('victron')


async def write_to_influx(dbhost, dbport, dbname='victron'):
    global client
    global datapoint
    global reg_block

    def trunc_float(floatval):
        return float('%.2f' % floatval)

    try:
        solar_client = InfluxDBClient(host=dbhost, port=dbport, db=dbname)
        await solar_client.create_database(db=dbname)
    except ClientConnectionError as e:
        logger.error(f'Error during connection to InfluxDb {dbhost}: {e}')
        return

    logger.info('Database opened and initialized')
    while True:
        try:
            reg_block = {}
            reg_block = client.read_holding_registers(800, 27)
            if reg_block:
                datapoint = {
                    'measurement': 'Victron',
                    'tags': {},
                    'fields': {}
                }
                # print(reg_block)
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

                
                datapoint['tags']['system'] = 1

                # AC Consumption
                logger.debug(f'Block17: {str(reg_block[17])}')
                logger.debug(f'Block18: {str(reg_block[18])}')
                logger.debug(f'Block19: {str(reg_block[19])}')
                scalefactor = 1
                datapoint['fields']['AC Consumption L1'] = trunc_float(reg_block[17] * scalefactor)
                datapoint['fields']['AC Consumption L2'] = trunc_float(reg_block[18] * scalefactor)
                datapoint['fields']['AC Consumption L3'] = trunc_float(reg_block[19] * scalefactor)

                # Grid
                logger.debug(f'Block17: {str(reg_block[20])}')
                logger.debug(f'Block18: {str(reg_block[21])}')
                logger.debug(f'Block19: {str(reg_block[22])}')
                scalefactor = 1
                datapoint['fields']['Grid L1'] = trunc_float(np.int16(reg_block[20]) * scalefactor)
                datapoint['fields']['Grid L2'] = trunc_float(np.int16(reg_block[21]) * scalefactor)
                datapoint['fields']['Grid L3'] = trunc_float(np.int16(reg_block[22]) * scalefactor)

                # PV On Input
                logger.debug(f'Block11: {str(reg_block[11])}')
                logger.debug(f'Block12: {str(reg_block[12])}')
                logger.debug(f'Block13: {str(reg_block[13])}')
                scalefactor = 1
                datapoint['fields']['PV - AC-coupled on input L1'] = trunc_float(reg_block[11] * scalefactor)
                datapoint['fields']['PV - AC-coupled on input L2'] = trunc_float(reg_block[12] * scalefactor)
                datapoint['fields']['PV - AC-coupled on input L3'] = trunc_float(reg_block[13] * scalefactor)

                # PV On Output
                logger.debug(f'Block8: {str(reg_block[8])}')
                logger.debug(f'Block9: {str(reg_block[9])}')
                logger.debug(f'Block10: {str(reg_block[10])}')
                scalefactor = 1
                datapoint['fields']['PV - AC-coupled on output L1'] = trunc_float(reg_block[8] * scalefactor)
                datapoint['fields']['PV - AC-coupled on output L2'] = trunc_float(reg_block[9] * scalefactor)
                datapoint['fields']['PV - AC-coupled on output L3'] = trunc_float(reg_block[10] * scalefactor)


                datapoint['time'] = str(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat())
                logger.debug(f'Writing to Influx: {str(datapoint)}')

                await solar_client.write(datapoint)

            else:
                # Error during data receive
                if client.last_error() == 2:
                    logger.error(f'Failed to connect to Victron Host {client.host()}!')
                elif client.last_error() == 3 or client.last_error() == 4:
                    logger.error('Send or receive error!')
                elif client.last_error() == 5:
                    logger.error('Timeout during send or receive operation!')

            reg_block = {}
            reg_block = client.read_holding_registers(840, 7)
            if reg_block:
                datapoint = {
                    'measurement': 'Victron',
                    'tags': {},
                    'fields': {}
                }                    
                # print(reg_block)
                # reg_block[0] = Battery Voltage (System)
                # reg_block[1] = Battery Current (System)
                # reg_block[2] = Battery Power (System)
                # reg_block[3] = Battery State of Charge (System)
                # reg_block[4] = Battery state (System)
                # reg_block[5] = Battery Consumed Amphours (System)
                # reg_block[6] = Battery Time to Go (System)

                # Battery Voltage
                logger.debug(f'Block0: {str(reg_block[0])}')
                scalefactor = 0.1
                datapoint['fields']['Battery Voltage'] = trunc_float(reg_block[0] * scalefactor)

                # Battery Current
                logger.debug(f'Block1: {str(reg_block[1])}')
                scalefactor = 0.1
                datapoint['fields']['Battery Current'] = trunc_float(np.int16(reg_block[1]) * scalefactor)

                # Battery Power
                logger.debug(f'Block2: {str(reg_block[2])}')
                scalefactor = 1
                datapoint['fields']['Battery Power'] = trunc_float(np.int16(reg_block[2]) * scalefactor)

                # Battery State of Charge
                logger.debug(f'Block3: {str(reg_block[3])}')
                scalefactor = 1
                datapoint['fields']['Battery State of Charge'] = trunc_float(reg_block[3] * scalefactor)

                
                datapoint['time'] = str(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat())
                logger.debug(f'Writing to Influx: {str(datapoint)}')

                await solar_client.write(datapoint)


            else:
                # Error during data receive
                if client.last_error() == 2:
                    logger.error(f'Failed to connect to Victron Host {client.host()}!')
                elif client.last_error() == 3 or client.last_error() == 4:
                    logger.error('Send or receive error!')
                elif client.last_error() == 5:
                    logger.error('Timeout during send or receive operation!')               
                
                
                
                
        except InfluxDBWriteError as e:
            logger.error(f'Failed to write to InfluxDb: {e}')
        except IOError as e:
            logger.error(f'I/O exception during operation: {e}')
        except Exception as e:
            logger.error(f'Unhandled exception: {e}')

        await asyncio.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--influxdb', default='localhost')
    parser.add_argument('--influxport', type=int, default=8086)
    parser.add_argument('--port', type=int, default=502, help='ModBus TCP port number to use')
    parser.add_argument('--unitid', type=int, default=100, help='ModBus unit id to use in communication')
    parser.add_argument('venus', metavar='Venus IP', help='IP address of the Venus Device to monitor')
    parser.add_argument('--debug', '-d', action='count')
    args = parser.parse_args()

    logging.basicConfig()
    if args.debug and args.debug >= 1:
        logging.getLogger('victron').setLevel(logging.DEBUG)
    if args.debug and args.debug == 2:
        logging.getLogger('aioinflux').setLevel(logging.DEBUG)

    print('Starting up Victron Venus monitoring')
    print(f'Connecting to Victron Venus {args.venus} on port {args.port} using unitid {args.unitid}')
    print(f'Writing data to influxDb {args.influxdb} on port {args.influxport}')
    client = ModbusClient(args.venus, port=args.port, unit_id=args.unitid, auto_open=True)
    logger.debug('Running eventloop')
    asyncio.get_event_loop().run_until_complete(write_to_influx(args.influxdb, args.influxport))

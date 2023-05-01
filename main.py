from heater import Heater, Heaters
from machine import Pin, ADC, RTC
from time import localtime, gmtime

from umodbus.serial import ModbusRTU as ModbusSlave
from registers import register_definitions, callback

from _thread import start_new_thread, allocate_lock

import logging
global log

log = logging.getLogger()
LOG = "log.txt"

format = "%(asctime)s %(cputemp)s %(levelname)s %(message)s"
logging.basicConfig(level=logging.NOTSET, format=format, stream=logging.printstream)

lock = allocate_lock()

def cputemp_read() -> float:
    chip_temp = ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = chip_temp.read_u16() * conversion_factor 
    cputemp = 27.0 - (reading - 0.706)/0.001721
    return cputemp

## SSR outputs
heaters = Heaters(50)
heaters.add_heater(Heater(16))
heaters.add_heater(Heater(18))
heaters.add_heater(Heater(22))
heaters.add_heater(Heater(20))

## Modbus slave
tx_led = Pin(25, Pin.OUT)
slave_config = {
    'addr': 27,
    'uart_id': 0,
    'pins': (Pin(0), Pin(1)),  # (TX, RX)
    'baudrate': 19200,
    'data_bits': 8,
    'parity': None,#0, #0 for Even
    'stop_bits': 1,
    'ctrl_pin': 2,
    'logger':log
}


log.info("Starting Modbus slave")
slave = ModbusSlave(**slave_config)
slave._itf.tx_led = tx_led
slave.setup_registers(register_definitions)

def run():
    log.info("Starting Heaters thread")
    while True:
        with lock:
            heaters.update()

def set_power(heater, power):
    with lock:
        heaters.set_power(heater,power)

def set_active(heater,active):
    with lock:
        heaters.on(heater) if active else heaters.off(heater)

def set_H1_power(reg_type, address, val):
    log.info("Setting H1 power: {}".format(val[0]))
    set_power(0,val[0])

def set_H2_power(reg_type, address, val):
    log.info("Setting H2 power: {}".format(val[0]))
    set_power(1,val[0])

def set_H3_power(reg_type, address, val):
    log.info("Setting H3 power: {}".format(val[0]))
    set_power(2,val[0])

def set_H4_power(reg_type, address, val):
    log.info("Setting H4 power: {}".format(val[0]))
    set_power(3,val[0])

def set_status(reg_type, address, val):
    log.info("Setting status: {}".format(bin(val[0])))
    set_active(0,val[0] & 0x01)
    set_active(1,val[0] & 0x02)
    set_active(2,val[0] & 0x04)
    set_active(3,val[0] & 0x08)

def set_grid_frequency(reg_type, address, val):
    log.info("Setting grid frequency: {}".format(val[0]))
    lock.acquire()
    heaters.set_grid_frequency(val[0])
    lock.release()

def Log_File_Read(reg_type, address, vals):
    with open(LOG, 'r') as f:
        buff = f.read()
        bytes_to_send = buff[:len(vals)*2 if len(buff) > len(vals)*2 else len(buff)]
        values = []
        for i in range(0, len(bytes_to_send), 2):
            values.append(int.from_bytes(bytes_to_send[i:i+2].encode("ascii"),"big"))
        if len(values) < len(vals):
            values.extend( [0]*(len(vals)-len(values)))
        slave.set_hreg(10, values)
        buff = buff[len(values)*2:]
    with open(LOG, 'w+') as f:
        f.write(buff)

callback.reg_set_heater1_power = set_H1_power
callback.reg_set_heater2_power = set_H2_power
callback.reg_set_heater3_power = set_H3_power
callback.reg_set_heater4_power = set_H4_power
callback.reg_set_status = set_status
callback.reg_set_grid_frequency = set_grid_frequency
callback.reg_Log_File_Read = Log_File_Read

start_new_thread(run, ())


try:
    while True:
        slave.set_hreg(6, int(cputemp_read()*100))
        slave.process()
except Exception as e:
    log.exception("Exception in main loop: {}".format(e))
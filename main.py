from heater import Heater, Heaters
from machine import Pin, ADC

from umodbus.serial import ModbusRTU as ModbusSlave
from registers import register_definitions, callback

from _thread import start_new_thread, allocate_lock

lock = allocate_lock()

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
    'parity': 0, #0 for Even
    'stop_bits': 1,
    'ctrl_pin': 2
}



slave = ModbusSlave(**slave_config)
slave._itf.tx_led = tx_led
slave.setup_registers(register_definitions)

def run():
    while True:
        lock.acquire()
        heaters.update()
        lock.release()

def set_power(heater, power):
    lock.acquire()
    heaters.set_power(heater,power)
    lock.release()

def set_active(heater,active):
    lock.acquire()
    if active:
        heaters.on(heater)
    else:
        heaters.off(heater)
    lock.release()

def set_H1_power(reg_type, address, val):
    set_power(0,val[0])

def set_H2_power(reg_type, address, val):
    set_power(1,val[0])

def set_H3_power(reg_type, address, val):
    set_power(2,val[0])

def set_H4_power(reg_type, address, val):
    set_power(3,val[0])

def set_status(reg_type, address, val):
    set_active(0,val[0] & 0x01)
    set_active(1,val[0] & 0x02)
    set_active(2,val[0] & 0x04)
    set_active(3,val[0] & 0x08)

def set_grid_frequency(reg_type, address, val):
    lock.acquire()
    heaters.set_grid_frequency(val[0])
    lock.release()

callback.reg_set_heater1_power = set_H1_power
callback.reg_set_heater2_power = set_H2_power
callback.reg_set_heater3_power = set_H3_power
callback.reg_set_heater4_power = set_H4_power
callback.reg_set_status = set_status
callback.reg_set_grid_frequency = set_grid_frequency

start_new_thread(run, ())

chip_temp = ADC(4)
conversion_factor = 3.3 / (65535)

while True:
    reading = chip_temp.read_u16() * conversion_factor 
    temperature = 27 - (reading - 0.706)/0.001721
    slave.set_hreg(6, int(temperature*10))
    slave.process()
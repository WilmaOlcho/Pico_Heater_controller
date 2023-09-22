from heater import Heater, Heaters
from machine import Pin, ADC, Timer
from time import sleep_ms, ticks_us, ticks_diff

from umodbus.serial import ModbusRTU as ModbusSlave
from registers import register_definitions, callback

from _thread import start_new_thread, allocate_lock

from ledstrip import IC74HC595, LedStrip

sr = IC74HC595(11,12,13,10)
leds = LedStrip(8, sr, direction=-1, leds_as_indicator=8)
leds.percent_to_led(100,leds.green)
leds = LedStrip(8, sr, direction=-1, leds_as_indicator=6)

#import logging
#global log

#log = logging.getLogger()
#LOG = "log.txt"

#format = "%(asctime)s %(cputemp)s %(levelname)s %(message)s"
#logging.basicConfig(level=logging.NOTSET, format=format, stream=logging.printstream)

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
    #'logger':log
}


#log.info("Starting Modbus slave")
slave = ModbusSlave(**slave_config)
slave._itf.tx_led = tx_led
slave.setup_registers(register_definitions)

class PeriodicTimer:
    _timer:int
    active:bool
    period:float
    def __init__(self, callback):
        self.active = False
        self.callback = callback

    def start(self, period:float) -> None:
        self._timer = ticks_us()
        self.active = True
        self.period = period

    def stop(self) -> None:
        self.active = False

    def restart(self) -> None:
        self.start(self.period)

    def update(self) -> None:
        if self.active:
            if (abs(ticks_diff(self._timer,ticks_us())) > self.period * 1000000):
                self._timer = ticks_us()
                self.callback()


timerjump = 0
def leds_timer_cb():
    global timerjump
    with lock:
        powers = [heaters.get_power(i) for i in range(4)]
    
    ledmark1 = timerjump%4 & 0x1
    ledmark2 = timerjump%4 & 0x2
    for i, mark in enumerate([ledmark1, ledmark2]):
        if mark:
            leds.leds[i].green()
        else:
            leds.leds[i].off()
    leds.percent_to_led(powers[timerjump%4],leds.red)
    timerjump+=1

leds_timer = PeriodicTimer(leds_timer_cb)

def run():
    leds_timer.start(1.0)
    #log.info("Starting Heaters thread")
    while True:
        with lock:
            heaters.update()
        leds_timer.update()

class Heater_control:
    def __init__(self, heaters:Heaters, lock, *args, **kwargs):
        self.heaters = heaters
        self.lock = lock
        self.timer = PeriodicTimer(self._timer_cb)
        self.timer.start(10.0)

    def _timer_cb(self):
        self.stop_processing(0,0,[0],_no_restart=True)
        self.timer.start(10.0)

    def stop_processing(self, reg_type, address, val, _no_restart=False):
        self.set_status(reg_type, address, [0],_no_restart=_no_restart)

    def set_power(self, heater, power, _no_restart=False):
        if not _no_restart:
            self.timer.restart()
        with self.lock:
            self.heaters.set_power(heater,power)

    def set_active(self, heater,active, _no_restart=False):
        if not _no_restart:
            self.timer.restart()
        with self.lock:
            self.heaters.on(heater) if active else heaters.off(heater)

    def set_H1_power(self, reg_type, address, val, _no_restart=False):
        #log.info("Setting H1 power: {}".format(val[0]))
        self.set_power(0,val[0], _no_restart=_no_restart)

    def set_H2_power(self, reg_type, address, val, _no_restart=False):
        #log.info("Setting H2 power: {}".format(val[0]))
        self.set_power(1,val[0], _no_restart=_no_restart)

    def set_H3_power(self, reg_type, address, val, _no_restart=False):
        #log.info("Setting H3 power: {}".format(val[0]))
        self.set_power(2,val[0], _no_restart=_no_restart)

    def set_H4_power(self, reg_type, address, val, _no_restart=False):
        #log.info("Setting H4 power: {}".format(val[0]))
        self.set_power(3,val[0], _no_restart=_no_restart)

    def set_status(self, reg_type, address, val ,_no_restart=False):
        #log.info("Setting status: {}".format(bin(val[0])))
        self.set_active(0,val[0] & 0x01 ,_no_restart=_no_restart)
        self.set_active(1,val[0] & 0x02 ,_no_restart=_no_restart)
        self.set_active(2,val[0] & 0x04 ,_no_restart=_no_restart)
        self.set_active(3,val[0] & 0x08 ,_no_restart=_no_restart)

    def set_grid_frequency(self, reg_type, address, val, _no_restart=False):
        if not _no_restart:
            self.timer.restart()
        #log.info("Setting grid frequency: {}".format(val[0]))
        with self.lock:
            self.heaters.set_grid_frequency(val[0])

    def Log_File_Read(self, reg_type, address, vals, _no_restart=False):
        if not _no_restart:
            self.timer.restart()
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

Heaters_control = Heater_control(heaters, lock)

callback.reg_set_heater1_power = Heaters_control.set_H1_power
callback.reg_set_heater2_power = Heaters_control.set_H2_power
callback.reg_set_heater3_power = Heaters_control.set_H3_power
callback.reg_set_heater4_power = Heaters_control.set_H4_power
callback.reg_set_status = Heaters_control.set_status
callback.reg_set_grid_frequency = Heaters_control.set_grid_frequency
callback.reg_Log_File_Read = Heaters_control.Log_File_Read
callback.reg_set_stop_processing = Heaters_control.stop_processing

start_new_thread(run, ())

try:
    while True:
        slave.set_hreg(6, int(cputemp_read()*100))
        slave.process()
        Heaters_control.timer.update()
except Exception as e:
    print(e)
    #log.exception("Exception in main loop: {}".format(e))
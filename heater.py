from machine import Pin
from utime import ticks_us, ticks_diff

class Heater:
    power:int
    active:bool
    _high:int
    _low:int
    _timer:int
    _counter:int
    _grid_frequency:int

    def __init__(self, pin:int):
        self.pin = Pin(pin, Pin.OUT)
        self.pin.value(0)
        self.power = 0
        self.active = False
        self._high = 0
        self._low = 1
        self._timer = ticks_us()
        self._grid_frequency = 50

    def set_grid_frequency(self, frequency:int) -> None:
        self._grid_frequency = frequency

    def on(self) -> None:
        self.active = True

    def off(self) -> None:
        self.active = False

    def _calculate_times(self) -> None:
        percentage = float(self.power) / 100
        self._high = 0
        self._low = 1
        while abs(float(self._high) / float(self._high+self._low) - percentage) > 0.001:
            if float(self._high) / float(self._high+self._low) > percentage:
                self._low += 1
            if float(self._high) / float(self._high+self._low) < percentage:
                self._high += 1

    def set_power(self, power:int) -> None:
        self.power = power
        self._calculate_times()

    def update(self) -> None:
        if self.active:
            if (ticks_diff(self._timer,ticks_us()) > (1/self._grid_frequency) * 500000):
                self._timer = ticks_us()
                if self._counter < self._high:
                    self.pin.value(1)
                    self._counter += 1
                elif self._counter < self._high + self._low:
                    self.pin.value(0)
                    self._counter += 1
                else:
                    self._counter = 0
        else:
            self.pin.value(0)
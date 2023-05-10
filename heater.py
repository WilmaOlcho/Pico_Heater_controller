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
        self._counter = 0

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
            if (abs(ticks_diff(self._timer,ticks_us())) > (1/self._grid_frequency) * 1000000):
                self._timer = ticks_us()
                if self._counter < self._high:
                    self.pin.value(1)
                elif self._counter < self._high + self._low:
                    self.pin.value(0)
                self._counter += 1
                if self._counter >= self._high + self._low:
                    self._counter = 0
        else:
            self.pin.value(0)

class Heaters:
    heaters = []
    _grid_frequency:int
    def __init__(self, grid_frequency:int = 50):
        self._grid_frequency = grid_frequency

    def add_heater(self, heater:Heater) -> None:
        self.heaters.append(heater)
        heater.set_grid_frequency(self._grid_frequency)

    def set_grid_frequency(self, frequency:int) -> None:
        self._grid_frequency = frequency
        for heater in self.heaters:
            heater.set_grid_frequency(self._grid_frequency)

    def set_power(self, heater:int, power:int) -> None:
        self.heaters[heater].set_power(power)

    def get_power(self, heater:int) -> int:
        return self.heaters[heater].power

    def on(self, heater:int) -> None:
        self.heaters[heater].on()

    def off(self, heater:int) -> None:
        self.heaters[heater].off()

    def set_power_all(self, power:int) -> None:
        for heater in self.heaters:
            heater.set_power(power)

    def on_all(self) -> None:
        for heater in self.heaters:
            heater.on() 

    def off_all(self) -> None:
        for heater in self.heaters:
            heater.off()

    def update(self) -> None:
        for heater in self.heaters:
            heater.update()

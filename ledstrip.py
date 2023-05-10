from machine import Pin

class IC74HC595:
    def __init__(self, data_pin, latch_pin, clock_pin, oe_pin):
        self.data_pin = Pin(data_pin, Pin.OUT)
        self.latch_pin = Pin(latch_pin, Pin.OUT)
        self.clock_pin = Pin(clock_pin, Pin.OUT)
        self.oe_pin = Pin(oe_pin, Pin.OUT)

    def write(self, data):
        #self.oe_pin.on()
        self.clock_pin.off()
        self.latch_pin.off()
        self.clock_pin.on()
        for i in range(len(data)):
            self.clock_pin.off()
            self.data_pin.value(data[i] & 1)
            self.clock_pin.on()
        self.clock_pin.off()
        self.latch_pin.on()
        self.clock_pin.on()
        self.oe_pin.off()

class LedStrip:
    class led:
        def __init__(self):
            self.state = [0,0]
        def red(self):
            self.state = [0,1]
        def green(self):
            self.state = [1,0]
        def off(self):
            self.state = [0,0]
    red = 1
    green = 2
    def __init__(self, length:int, sr: IC74HC595, direction: int = 1, leds_as_indicator=6):
        self.sr = sr
        self.leds = []
        self.direction = direction
        self.leds_as_indicator = leds_as_indicator
        for _ in range(length):
            self.leds.append(self.led())

    def update(self):
        data = []
        for i in range(len(self.leds)):
            data += self.leds[i if self.direction==1 else len(self.leds)-i-1].state
        self.sr.write(data)

    def percent_to_led(self, prcnt, color):
        active_leds = round(prcnt * self.leds_as_indicator / 100)
        for i, led in enumerate(self.leds):
            if i < len(self.leds) - self.leds_as_indicator:
                continue
            if i < active_leds + len(self.leds) - self.leds_as_indicator:
                if color == self.red:
                    led.red()
                elif color == self.green:
                    led.green()
            else:
                self.leds[i].off()
        self.update()




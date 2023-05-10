from ledstrip import IC74HC595, LedStrip

sr = IC74HC595(11,12,13,10)
leds = LedStrip(8, sr, direction=1, leds_as_indicator=8)
leds.percent_to_led(100,leds.green)
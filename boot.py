import webrepl
webrepl.start()

import machine

import neopixel
rgb = neopixel.NeoPixel(machine.Pin(27, machine.Pin.OUT), 1)
rgb[0] = (0,0,0)
rgb.write()

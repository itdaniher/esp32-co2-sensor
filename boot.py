import machine

import neopixel
import micropython

micropython.alloc_emergency_exception_buf(256)

rgb = neopixel.NeoPixel(machine.Pin(27, machine.Pin.OUT), 1)
rgb[0] = (0, 0, 0)
rgb.write()

machine.freq(240000000)

import math
import random
import time
import machine
import neopixelrmt
import _thread
import esp32
import socket

rgb_strand = neopixelrmt.NeoPixel(machine.Pin(26, machine.Pin.OUT), 200)

rainbow = [
    (148, 0, 211),
    (75, 0, 130),
    (0, 0, 255),
    (0, 255, 0),
    (255, 255, 0),
    (255, 127, 0),
    (255, 0, 0),
    (0, 0, 0),
]


def chase(color=rainbow[0], max_count=None, sleep=0.01):
    for i in range(max_count or rgb_strand.n):
        rgb_strand[i - 1] = rainbow[-1]
        rgb_strand[i] = color
        rgb_strand.write()
        time.sleep(sleep)


exit_pretty = False


def stop_pretty():
    global exit_pretty
    exit_pretty = True


def start_pretty():
    global exit_pretty
    exit_pretty = False
    _thread.start_new_thread(pretty_forever, (rgb_strand,))


@micropython.native
def pretty_forever(neopixels):
    global exit_pretty
    ct = neopixels.n
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", 2812))
    while not exit_pretty:
        ts = time.ticks_us() / 1e6
        #rgbvals, address = s.recvfrom(neopixels.n * 3)
        s.readinto(neopixels.buf, neopixels.n * 3)
        neopixels.write()

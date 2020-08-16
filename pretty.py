import math
import random
import time


@micropython.native
def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)  # XXX assume int() truncates!
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q
    # Cannot get here


@micropython.native
def get_hsv(ts, i):
    h = 0.5
    h += 0.3 * math.cos((ts * 1.001 + 0.2 * i))
    # h += 0.4 * math.sin((ts * 1.002 + 0.1 * i))
    if h < 0.0:
        h += 1.0
    h *= 0.5
    s = 0.8
    v = 0.1
    return h, s, v


@micropython.native
def pretty(neopixels, rtc):
    ct = neopixels.n
    # hh, mm, ss, us = rtc.datetime()[-4:]
    # ts = hh*3600 + mm * 60 + ss + us / 1e6
    ts = time.ticks_us() / 1e6
    for i in range(ct):
        h, s, v = get_hsv(ts, i)
        if random.random() < 0.10:
            v = 0.2
        r, g, b = hsv_to_rgb(h, s, v)
        neopixels[i] = int(r * 255), int(g * 255), int(b * 255)
    neopixels.write()
    return ts
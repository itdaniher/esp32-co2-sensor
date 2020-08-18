import gc
import ntptime
import network
import time

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

APs = sta_if.scan()
AP_names = [x[0] for x in APs]

known_APs = {b"dev101-testing": b"dev101-testing"}

for AP_name in AP_names:
    if AP_name in known_APs:
        sta_if.connect(AP_name, known_APs[AP_name])
        break


rtc = machine.RTC()


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

connect_count = 100
while not sta_if.isconnected():
    for color in rainbow:
        rgb[0] = color
        rgb.write()
        time.sleep(0.1)
        connect_count -= 1
    if connect_count < 0:
        rgb[0] = rainbow[-2]
        rgb.write()
        break

my_ip = sta_if.ifconfig()[0]
if "192.168" in my_ip:
    rgb[0] = rainbow[3]
    rgb.write()
    try:
        time.sleep(1)
        ntptime.settime()
        print("current time: " + str(rtc.datetime()))
    except Exception:
        print("failed to set time")

import mhz19b

uart = machine.UART(1, tx=26, rx=32, baudrate=9600)

mhz19 = mhz19b.MHZ19(uart)
mhz19.abc_off()
# prime mhz19
try:
    mhz19.read_all()
except:
    pass


def timestamp(t=None):
    return "%04u-%02u-%02uT%02u:%02u:%02u" % time.localtime(t)[0:6]


import picoweb, ujson

app = picoweb.WebApp(__name__)


@app.route("/")
def index(req, resp):
    await picoweb.start_response(resp)
    await resp.awrite("Hello world from picoweb running on the ESP32")


@app.route("/timestamp")
def index(req, resp):
    await picoweb.start_response(resp)
    await resp.awrite(timestamp())


@app.route("/reset")
def index(req, resp):
    def reset_in(seconds):
        time.sleep(seconds)
        machine.reset()

    _thread.start_new_thread(reset_in, (30,))
    await picoweb.start_response(resp)
    await resp.awrite("resetting in 30 seconds")


@app.route("/co2")
def index(req, resp):
    await picoweb.jsonify(resp, mhz19.read_all())


@app.route("/calibrate")
def index(req, resp):
    mhz19.zero_point_calibration()
    await picoweb.start_response(resp)
    await resp.awrite("Calibrating MHZ19B. Ensure sensor placed in fresh air.")


import _thread

_thread.start_new_thread(app.run, (), dict(debug=True, host=my_ip, port=80))

import uftpd
import utelnetserver

utelnetserver.start()

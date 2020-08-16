import gc
import socket
import time

import _thread
import network
import ntptime
import ujson

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

APs = sta_if.scan()
AP_names = [x[0] for x in APs]

known_APs = {b"dev101-testing": b"dev101-testing"}

for AP_name in AP_names:
    if AP_name in known_APs:
        sta_if.connect(AP_name, known_APs[AP_name], listen_interval=-1)
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


def timestamp(t=None):
    return str(rtc.datetime())


import picoweb

app = picoweb.WebApp(__name__)


@app.route("/")
def index(req, resp):
    await picoweb.start_response(resp)
    await resp.awrite("Hello world from picoweb running on the ESP32")


@app.route("/timestamp")
def index(req, resp):
    await picoweb.start_response(resp)
    await resp.awrite(timestamp())


@app.route("/echo")
def index(req, resp):
    size = int(req.headers[b"Content-Length"])
    data = await req.reader.readexactly(size)
    await picoweb.start_response(resp)
    await resp.awrite(data)


@app.route("/reset")
def index(req, resp):
    def reset_in(seconds):
        time.sleep(seconds)
        machine.reset()

    _thread.start_new_thread(reset_in, (30,))
    await picoweb.start_response(resp)
    await resp.awrite("resetting in 30 seconds")


web_thread = _thread.start_new_thread(
    app.run, (), dict(debug=False, host=my_ip, port=80)
)

exit_echo = False


@micropython.native
def echo():
    global exit_echo
    exit_echo = False
    addr = socket.getaddrinfo("0.0.0.0", 81)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(0)
    socket_buffer = bytearray(4096)
    while not exit_echo:
        cl, addr = s.accept()
        print("accepting: " + str(addr))
        cl.settimeout(0.1)
        while not exit_echo:
            try:
                n = cl.readinto(socket_buffer)
                cl.write(memoryview(socket_buffer)[:n])
            except:
                break
        cl.close()
    s.close()


_thread.start_new_thread(echo, ())

output_pin = machine.Pin(32, mode=machine.Pin.OUT, value=0)
input_pin = machine.Pin(39, mode=machine.Pin.IN)
input_pin.irq(lambda p: output_pin(1))
exit_timer = False
on_minutes = [1, 2, 3, 4, 5]


def hourly_timer():
    global exit_timer
    global on_minutes
    global output_pin
    while not exit_timer:
        hours, minutes, seconds, microseconds = rtc.datetime()[-4:]
        if minutes in on_minutes:
            output_pin(1)
        else:
            output_pin(0)
        time.sleep(10)


_thread.start_new_thread(hourly_timer, ())

import uftpd
import utelnetserver

utelnetserver.start()

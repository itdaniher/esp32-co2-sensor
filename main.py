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

import utelnetserver
import uftpd

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


@app.route("/repl")
def redir(req, resp):
    import webrepl_cfg

    host = req.headers.get(b"Host", my_ip.encode()).decode()
    password = webrepl_cfg.PASS
    await picoweb.start_response(
        resp,
        status="302",
        headers="Location: http://%s/repl_static#%s:8266;%s" % (host, host, password),
    )
    await resp.awrite("\r\n")


@app.route("/repl_static")
def index(req, resp):
    headers = b"Cache-Control: max-age=86400\r\n"
    # assert b"gzip" in req.headers.get(b"Accept-Encoding", b"")
    headers += b"Content-Encoding: gzip\r\n"
    await app.sendfile(resp, "webrepl2.html.gzip", "text/html", headers)


@app.route("/echo")
def index(req, resp):
    size = int(req.headers[b"Content-Length"])
    data = await req.reader.readexactly(size)
    await picoweb.start_response(resp)
    await resp.awrite(data)


import _thread

web_thread = _thread.start_new_thread(
    app.run, (), dict(debug=True, host=my_ip, port=80)
)
import neopixelrmt

rgb_strand = neopixelrmt.NeoPixel(machine.Pin(26, machine.Pin.OUT), 200)


def chase(color=rainbow[0], max_count=None, sleep=0.01):
    for i in range(max_count or rgb_strand.n):
        rgb_strand[i - 1] = rainbow[-1]
        rgb_strand[i] = color
        rgb_strand.write()
        time.sleep(sleep)


import pretty

exit_pretty = False


def pretty_forever():
    global exit_pretty
    last_timestamp = pretty.pretty(rgb_strand, rtc)
    while not (exit_pretty or utelnetserver.connected):
        timestamp = pretty.pretty(rgb_strand, rtc)
        delta  = (timestamp - last_timestamp)
        last_timestamp = timestamp
        if exit_pretty:
            break


def stop_pretty():
    global exit_pretty
    exit_pretty = True


def start_pretty():
    global exit_pretty
    exit_pretty = False
    _thread.start_new_thread(pretty_forever, ())



start_pretty()

exit_echo = False

import socket


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
exit_timer = False
def hourly_timer(output_pin, on_minutes = (1,2)):
    global exit_timer
    while exit_timer:
        hours, minutes, seconds, microseconds = rtc.datetime()[-4:]
        if minutes in on_minutes:
            output_pin.on()
        else:
            output_pin.off()
        time.sleep(10)

#_thread.start_new_thread(hourly_timer, (output_pin, (1,2)))

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
uart = machine.UART(1, tx=26, rx=32, baudrate=9600)


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

mhz19 = mhz19b.MHZ19(uart)
# prime mhz19
try:
    mhz19.read()
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


@app.route("/co2")
def index(req, resp):
    await picoweb.jsonify(resp, mhz19.read_all())


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


import _thread

_thread.start_new_thread(app.run, (), dict(debug=True, host=my_ip, port=80))

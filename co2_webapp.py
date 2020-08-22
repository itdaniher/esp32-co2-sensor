import machine
import picoweb

app = picoweb.WebApp("Co2 Sensor")

import mhz19b
uart = machine.UART(1, tx=26, rx=32, baudrate=9600)

mhz19 = mhz19b.MHZ19(uart)
mhz19.abc_off()
# prime mhz19
try:
    mhz19.read_all()
except:
    pass

@app.route("/")
def index(req, resp):
    await picoweb.jsonify(resp, mhz19.read_all())


@app.route("/calibrate")
def index(req, resp):
    mhz19.zero_point_calibration()
    await picoweb.start_response(resp)
    await resp.awrite("Calibrating MHZ19B. Ensure sensor placed in fresh air.")

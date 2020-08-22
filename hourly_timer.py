import machine
import time
rtc = machine.RTC()
output_pin = machine.Pin(32, mode=machine.Pin.OUT, value=0)
input_pin = machine.Pin(39, mode=machine.Pin.IN)
input_pin.irq(lambda p: output_pin(1))

exit_timer = False
on_minutes = [1, 2, 3, 4, 5]

import picoweb

app = picoweb.WebApp("Adjustable timer.")

@app.route("/")
def index(req,resp):
    picoweb.jsonify(on_minutes, resp)

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

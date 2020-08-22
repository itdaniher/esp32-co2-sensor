import picoweb
import machine
import time
import ulid2
import _thread

app = picoweb.WebApp("basic ESP32 functionality")

@app.route("/")
def index(req, resp):
    await picoweb.start_response(resp)
    await resp.awrite("Hello world from picoweb running on the ESP32")

def timestamp(t=None):
    return "%04u-%02u-%02uT%02u:%02u:%02u" % time.localtime(t)[0:6]

@app.route("/timestamp")
def index(req, resp):
    await picoweb.start_response(resp)
    await resp.awrite(timestamp())

@app.route("/uid")
def index(req, resp):
    await picoweb.start_response(resp)
    uid = ulid2.encode_ulid_base32(b"\x00"*10+machine.unique_id())[-10:]
    await resp.awrite(uid)


@app.route("/debug")
def index(req,resp):
    open("debug.py", "wb").write("allowed=True")
    await picoweb.start_response(resp)
    await resp.awrite("Restart to enable debug file access and terminal via ftp and telnet.")

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


import _thread

import networking
station = networking.start_sta()
if station:
    access_point = False
else:
    access_point = networking.start_AP()

import debug
if debug.allowed:
    import uftpd
    import utelnetserver
    utelnetserver.start()

import picoweb
import co2_webapp
import base_webapp

site = picoweb.WebApp("everything")
site.mount("/", base_webapp.app)
site.mount("/co2", co2_webapp.app)

my_ip = (station or access_point).ifconfig()[0]

_thread.start_new_thread(site.run, (), dict(debug=True, host=my_ip, port=80))

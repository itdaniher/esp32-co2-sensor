import network
import ntptime
import machine
import neopixel
import time

rtc = machine.RTC()
rgb = neopixel.NeoPixel(machine.Pin(27, machine.Pin.OUT), 1)
rgb[0] = (0, 0, 0)
rgb.write()

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

import known_APs

def start_sta():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    APs = sta_if.scan()
    AP_names = [x[0] for x in APs]


    for AP_name in AP_names:
        if AP_name in known_APs.known_APs:
            sta_if.connect(AP_name, known_APs.known_APs[AP_name], listen_interval=-1)
            break


    connect_attempt_count = 100
    len_rainbow = len(rainbow)
    while (connect_attempt_count > 0) and not sta_if.isconnected():
        rgb[0] = rainbow[connect_attempt_count % len_rainbow]
        rgb.write()
        time.sleep(0.1)
        connect_attempt_count -= 1
    if connect_attempt_count <= 0:
        print("connect failed")
        rgb[0] = rainbow[-2]
        rgb.write()
        sta_if.active(False)
        return False
    else:
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
        return sta_if


def start_ap():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    ap_if.ifconfig(('192.168.0.254', '255.255.255.0', '192.168.0.254', '192.168.0.254'))
    ap_if.config(essid=known_APs.default_AP[0], channel=11, hidden=False, authmode=network.AUTH_WPA2_PSK, password=known_APs.default_AP[0], dhcp_hostname='192.168.0.254')
    from microDNSSrv import MicroDNSSrv
    MicroDNSSrv.Create({ '*' : '192.168.0.254' })

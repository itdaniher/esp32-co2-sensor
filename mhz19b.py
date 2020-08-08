# -*- coding: utf-8 -*-
# original: https://raw.githubusercontent.com/UedaTakeyuki/slider/master/mh_z19.py
#
# © Takeyuki UEDA 2015 -

import struct

# setting
version = "0.5.0"

# major version of running python
p_ver = "3"


class MHZ19:
    def __init__(self, ser):
        self.ser = ser

    def mh_z19(self):
        ser = self.ser
        while 1:
            result = ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
            s = ser.read(9)

            if p_ver == "2":
                if len(s) >= 4 and s[0] == "\xff" and s[1] == "\x86":
                    return {"co2": ord(s[2]) * 256 + ord(s[3])}
                break
            else:
                if len(s) >= 4 and s[0] == 0xFF and s[1] == 0x86:
                    return {"co2": s[2] * 256 + s[3]}
                break

    def read(self):
        result = self.mh_z19()
        if result is not None:
            return result

    def read_all(self):
        ser = self.ser
        while 1:
            result = ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
            s = ser.read(9)

            if p_ver == "2":
                if len(s) >= 9 and s[0] == "\xff" and s[1] == "\x86":
                    return {
                        "co2": ord(s[2]) * 256 + ord(s[3]),
                        "temperature": ord(s[4]) - 40,
                        "TT": ord(s[4]),
                        "SS": ord(s[5]),
                        "UhUl": ord(s[6]) * 256 + ord(s[7]),
                    }
                break
            else:
                if len(s) >= 9 and s[0] == 0xFF and s[1] == 0x86:
                    return {
                        "co2": s[2] * 256 + s[3],
                        "temperature": s[4] - 40,
                        "TT": s[4],
                        "SS": s[5],
                        "UhUl": s[6] * 256 + s[7],
                    }
                break

    def abc_on(self):
        ser = self.ser
        result = ser.write(b"\xff\x01\x79\xa0\x00\x00\x00\x00\xe6")

    def abc_off(self):
        ser = self.ser
        result = ser.write(b"\xff\x01\x79\x00\x00\x00\x00\x00\x86")

    def span_point_calibration(self, span):
        ser = self.ser
        if p_ver == "2":
            b3 = span / 256
        else:
            b3 = span // 256
        byte3 = struct.pack("B", b3)
        b4 = span % 256
        byte4 = struct.pack("B", b4)
        c = checksum([0x01, 0x88, b3, b4])
        request = b"\xff\x01\x88" + byte3 + byte4 + b"\x00\x00\x00" + c
        result = ser.write(request)

    def zero_point_calibration(self):
        ser = self.ser
        request = b"\xff\x01\x87\x00\x00\x00\x00\x00\x78"
        result = ser.write(request)

    def detection_range_5000(self):
        ser = self.ser
        request = b"\xff\x01\x99\x00\x00\x00\x13\x88\xcb"
        result = ser.write(request)

    def detection_range_2000(self):
        ser = self.ser
        request = b"\xff\x01\x99\x00\x00\x00\x07\xd0\x8F"
        result = ser.write(request)

    def checksum(array):
        return struct.pack("B", 0xFF - (sum(array) % 0x100) + 10)


if __name__ == "__main__":
    import serial
    import time
    import sys

    ser = serial.Serial(
        sys.argv[-1],
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1.0,
    )
    mhz = MHZ19(ser)
    while True:
        print(mhz.read_all())
        time.sleep(10)

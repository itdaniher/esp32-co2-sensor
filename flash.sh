sudo chown $USER /dev/ttyUSB0
pipenv run esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
pipenv run esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ./pycopy-esp32-3.1.5.bin

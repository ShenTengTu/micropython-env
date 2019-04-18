param($PORT)
$env:AMPY_PORT = $PORT # set ampy usb serial port as env

ampy put ../Env.py Env.py
ampy put env.json env.json
ampy put boot.py boot.py
ampy put main.py main.py
ampy ls -r
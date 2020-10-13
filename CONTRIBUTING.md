# Development guide
The development enviroment of the project only support **Linux** only.

It is strongly recommended to use a Python virtual environment for development.

## Make command
You can  execute `make` command in terminal (under the project directory) to display helping information.

## Micopython unix port
Before starting development, you need to compile Micopython unix port executable first, see [offcial GitHub Wiki] to setup.

After setup, you must set environment variable `MPY_PATH` as path of local MicroPython repository.

Environment variable`MPY_PATH` is used in shell script `bin/build_micropython.sh`.

Shell script `bin/build_micropython.sh` helps you to build MicroPython unix port by given version code.

The MicroPython executable and mpy-cross executable will be saved in "`$HOME/.micropython/bin`".

Shell script `bin/mpy_ver.sh`helps you to  switch MicroPython unix port version (includes mpy-cross).

## Micopython ESP32 port
We need  [esptool] to communicate with the ROM bootloader in ESP32.
```
pip install esptool 
```

We use [mpfshell] to interactive with file explorer on MicroPython board.
```
pip install mpfshell
```

Shell script `bin/esp-install-firmware.sh` would download the firmware to "`$HOME/.micropython/firmwares`", then use [esptool] to install the firmware to ESP32.
> See `install-firmware` target in `Makefile`.


[offcial GitHub Wiki]: https://github.com/micropython/micropython/wiki/Getting-Started
 [esptool]: https://github.com/espressif/esptool
[mpfshell]: https://github.com/wendlers/mpfshell


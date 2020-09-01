#!/bin/sh
# The firmware file will be stored at the application data folder of MicroPython unix port.
MPY_PATH="$HOME/.micropython"
FIRMWARE_PATH="$MPY_PATH/firmwares"

# Create directory "$FIRMWARE_PATH"  if not exist
[ ! -d "$FIRMWARE_PATH" ] && mkdir -p "$FIRMWARE_PATH"

# arg1 : firmware name
[ -z "$1" ] && { echo "1st argument must specify the firmware name." && exit; }
_micropython_firmware="$1"
_local_firmware="$FIRMWARE_PATH/$_micropython_firmware"
_remote_firmware="https://micropython.org/resources/firmware/$_micropython_firmware"

#  Download firmware if not exist
[ ! -f "$_local_firmware" ] && echo "Download $_micropython_firmware ..." && curl -# "$_remote_firmware" -o "$_local_firmware"

# Erase the entire flash
_port="${2:-/dev/ttyUSB0}"
esptool.py --chip esp32 --port "$_port" erase_flash

# Install
esptool.py --chip esp32 --port "$_port" --baud 460800 write_flash -z 0x1000 "$_local_firmware"
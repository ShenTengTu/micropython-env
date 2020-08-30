MICROPYTHON_FIRMWARE?=esp32-idf3-20191220-v1.12.bin
PORT?=/dev/ttyUSB0
MPFSHELL_PORT=ttyUSB0

# internal micropython script : dump test data
define _mpyc_0
import ujson
import btree
endef
export _mpyc_0

.PHONY: format install-firmware testing mpy-ls

format:
	@black .

install-firmware:
	@./bin/esp-install-firmware.sh $(MICROPYTHON_FIRMWARE) $(PORT)

testing: py-test mpy-unix-test

# Python 3.7.8
py-test:
	@echo "Testing - Python"
	@python -m tests.test_msgpack

# MicroPython (unix port) v1.12
mpy-unix-test:
	@echo "Testing - MicroPython (unix port)"
	@micropython -m tests.test_msgpack

# mpfshell
mpy-ls:
	@mpfshell --reset -n -c "open $(MPFSHELL_PORT);ls"
MICROPYTHON_FIRMWARE?=esp32-idf3-20191220-v1.12.bin
PORT?=/dev/ttyUSB0
MPFSHELL_PORT=ttyUSB0

fn_mpfs =mpfshell --reset -n -c  ${1}

mpy_init:=md lib;md lib/mpy_env
mpy_clean:=cd lib/mpy_env;mrm .+;cd /lib;rm mpy_env;cd /;rm lib;mrm .+
mpy_install:=cd lib/mpy_env;lcd mpy_env;mput \w+\.py;ls

offcial_msgpack=official.msgpack
custom_msgpack=mpy.msgpack

.PHONY: format install-firmware testing mpy-open mpy-ls mpy-clean mpy-init mpy-install mpy-put-test

format:
	@black .

install-firmware:
	@./bin/esp-install-firmware.sh $(MICROPYTHON_FIRMWARE) $(PORT)

testing: py-test mpy-unix-test msgpack-validation

# Python 3.7.8
py-test:
	@echo "[Testing - Python]"
	@python -m tests.test_msgpack

# MicroPython (unix port) v1.12
mpy-unix-test:
	@echo "[Testing - MicroPython (unix port)]"
	@micropython -m tests.test_msgpack

msgpack-validation:
	@echo "[MessagePack packages validation]"
	@echo "(CPython) Dump $(offcial_msgpack) by offcial package ..."
	@python -m msgpack_validation.official_dump
	@echo "(Micropython unix port) Dump $(custom_msgpack) by custom package ..."
	@micropython -m msgpack_validation.mpy_dump
	@echo "(CPython) Validate $(offcial_msgpack) & $(custom_msgpack) by offcial package ..."
	@python -m msgpack_validation.official_load
	@echo "(Micropython unix port) Validate $(offcial_msgpack) & $(custom_msgpack) by custom package ..."
	@micropython -m msgpack_validation.mpy_load
	@rm ./msgpack_validation/$(offcial_msgpack) && rm ./msgpack_validation/$(custom_msgpack)

# mpfshell
mpy-open:
	@mpfshell --reset -c "open $(MPFSHELL_PORT)"
mpy-ls:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);ls")
mpy-clean:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_clean)")
mpy-init:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_init)")
mpy-install:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_init);$(mpy_install)")
mpy-put-test:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);lcd tests;mput test_\w+\.py;ls")
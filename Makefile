MICROPYTHON_FIRMWARE?=esp32-idf3-20191220-v1.12.bin
PORT?=/dev/ttyUSB0
MPFSHELL_PORT=ttyUSB0

fn_mpfs =mpfshell --reset -n -c  ${1}

mpy_init:=md lib;md lib/mpy_env
mpy_clean:=cd lib/mpy_env;mrm .+;cd /lib;rm mpy_env;cd /;rm lib;mrm .+
mpy_install:=cd lib/mpy_env;lcd mpy_env;mput \w+\.py;ls

offcial_msgpack=official.msgpack
custom_msgpack=mpy.msgpack

# internal python script : dump "env.json" & "env.msgpack" for testing
define _pyc_0
import os
import json
from mpy_env import serialize
data = {"foo": True, "bar": 1000, "wee": [3.14159]}
cwd = os.getcwd()
with open(cwd  + "/env.json", "w+") as fp:
    fp.write(json.dumps(data))
with open(cwd  + "/env.msgpack", "w+b") as fp:
    fp.write(serialize(data))
print("dump 'env.json' & 'env.msgpack' for testing")
endef
export _pyc_0

.PHONY: format install-firmware testing mpy-open mpy-ls mpy-clean mpy-init mpy-install mpy-put-test mpy-put-example

format:
	@black .

install-firmware:
	@./bin/esp-install-firmware.sh $(MICROPYTHON_FIRMWARE) $(PORT)

testing: py-test mpy-unix-test msgpack-validation

# Python 3.7.8
py-test:
	@echo "[Testing - Python]"
	@python -m tests.test_msgpack
	@micropython -m tests.test_mpy_env

# MicroPython (unix port) v1.12
mpy-unix-test:
	@echo "[Testing - MicroPython (unix port)]"
	@micropython -m tests.test_msgpack
	@micropython -m tests.test_mpy_env

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
	@python -c "$$_pyc_0"
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);put env.json;put env.msgpack;lcd tests;mput test_\w+\.py;ls")
	@echo "remove local 'env.json' & 'env.msgpack'" && rm ./env.json &&rm ./env.msgpack
mpy-put-example:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);lcd examples;put env.json;mput \w+\.py;ls")

# distribution
sdist:
	@python setup.py sdist
sdist-clean:
	@rm -rf ./dist ./*egg-info ./MANIFEST
	
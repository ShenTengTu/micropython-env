include m_config.mk

MICROPYTHON_FIRMWARE?=esp32-idf3-20191220-v1.12.bin
PORT?=/dev/ttyUSB0
MPFSHELL_PORT=ttyUSB0

fn_mpfs =mpfshell --reset -n -c  ${1}

mpy_init:=md /lib;md /lib/mpy_env
mpy_clean:=cd /lib/mpy_env;mrm .+;cd /lib;rm mpy_env;cd /;rm lib;mrm .+
mpy_install:=cd /lib/mpy_env;lcd $(PWD)/mpy_env;mput \w+\.py
mpy_put_test:=cd /;lcd $(PWD);put env.json;put env.msgpack;lcd $(PWD)/tests;mput test_\w+\.py
mpy_put_example:=lcd $(PWD)/examples;put env.json;mput \w+\.py
mpy_testing=$(mpy_init);$(mpy_install);$(mpy_put_test);exec import test_msgpack;exec import test_mpy_env;$(mpy_clean)

offcial_msgpack=official.msgpack
custom_msgpack=mpy.msgpack

mpy_unix_build_versions=v1.12 v1.13
mpy_esp32_build_versions=esp32-idf3-20191220-v1.12.bin esp32-idf3-20200902-v1.13.bin

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

.PHONY: format build-mpy install-firmware testing mpy-testing-esp32 mpy-open mpy-ls mpy-clean mpy-init mpy-install mpy-put-test mpy-put-example sdist sdist-clean upload-pypi upload-testpypi

format:
	@black .

#  Build MicroPython unix port by given version code
build-mpy:
	@for i in $(mpy_unix_build_versions); do \
		echo "[Build MicroPython unix port $$i]" ; \
		./bin/build_micropython.sh $$i ; \
	done

install-firmware:
	@./bin/esp-install-firmware.sh $(MICROPYTHON_FIRMWARE) $(PORT)

testing: py-test mpy-unix-test msgpack-validation

# Python 3.7.8
py-test:
	@echo "[Testing - Python]"
	@python -m tests.test_msgpack
	@python -m tests.test_mpy_env

# MicroPython (unix port)
mpy-unix-test:
	@for i in $(mpy_unix_build_versions); do \
		echo "[Testing - MicroPython (unix port) $$i]" ; \
		./bin/mpy_ver.sh $$i ; \
		micropython -m tests.test_msgpack ; \
		micropython -m tests.test_mpy_env ; \
	done

msgpack-validation:
	@for i in $(mpy_unix_build_versions); do \
		echo "[MessagePack packages validation for MicroPython (unix port) $$i]" ; \
		./bin/mpy_ver.sh $$i ; \
		echo "(CPython) Dump $(offcial_msgpack) by offcial package ..." ; \
		python -m msgpack_validation.official_dump ; \
		echo "(Micropython unix port) Dump $(custom_msgpack) by custom package ..." ; \
		micropython -m msgpack_validation.mpy_dump ; \
		echo "(CPython) Validate $(offcial_msgpack) & $(custom_msgpack) by offcial package ..." ; \
		python -m msgpack_validation.official_load  ; \
		echo "(Micropython unix port) Validate $(offcial_msgpack) & $(custom_msgpack) by custom package ..." ; \
		micropython -m msgpack_validation.mpy_load ; \
		rm ./msgpack_validation/$(offcial_msgpack) && rm ./msgpack_validation/$(custom_msgpack) ; \
	done

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
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_init);$(mpy_install);ls")
mpy-put-test:
	@python -c "$$_pyc_0"
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_put_test);ls")
	@echo "remove local 'env.json' & 'env.msgpack'" && rm ./env.json &&rm ./env.msgpack
mpy-put-example:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_put_example);ls")
mpy-testing-esp32:
	@python -c "$$_pyc_0"
	@for fw in $(mpy_esp32_build_versions); do \
		echo "[Testing - MicroPython (ESP32) $$fw]" ; \
		./bin/esp-install-firmware.sh $$fw $(PORT) ; \
		$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_testing);") ; \
	done
	@echo "remove local 'env.json' & 'env.msgpack'" && rm ./env.json &&rm ./env.msgpack

# distribution
sdist:
	@python setup.py sdist
	@rm -rf ./dist/*.tar.gz.orig
sdist-clean:
	@rm -rf ./dist ./*egg-info ./MANIFEST
upload-pypi:
	@twine upload --repository pypi dist/*
upload-testpypi:
	@twine upload --repository testpypi dist/*

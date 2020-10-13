include m_config.mk
include m_mpfs_cmd.mk

.DEFAULT_GOAL := help
MICROPYTHON_FIRMWARE?=esp32-idf3-20191220-v1.12.bin
PORT?=/dev/ttyUSB0
MPFSHELL_PORT=ttyUSB0

mpy_put_env=cd /;lcd $(PWD);put env.json;put env.msgpack
mpy_rm_env=cd /;rm env.json;rm env.msgpack
mpy_upload_testing=$(mpy_mk_src_dirs);$(mpy_put_src_files);$(mpy_put_env);$(mpy_mk_tests_dirs);$(mpy_put_tests_files)
mpy_exec_testing=exec import tests.test_msgpack;exec import tests.test_mpy_env
mpy_clean_testing=$(mpy_rm_env);$(mpy_rm_tests);$(mpy_rm_src)

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

miscellaneous_targets:=help format build-mpy install-firmware
py_testing_targets:=py-test mpy-unix-test msgpack-validation
mpy_base_targets:=mpy-open mpy-ls
mpy_upload_targets:=mpy-upload-src mpy-upload-tests mpy-upload-examples
mpy_clean_targets:=mpy-clean-src mpy-clean-tests mpy-clean-examples
mpy_targets:=$(mpy_base_targets) $(mpy_upload_targets) $(mpy_clean_targets)
dist_targets:=sdist sdist-clean upload-pypi upload-testpypi
.PHONY: .FORCE_UPDATE  $(miscellaneous_targets) $(py_testing_targets) $(mpy_targets) $(dist_targets)
.FORCE_UPDATE:

# reference: https://gist.github.com/prwhite/8168133#gistcomment-2749866
help:
	@printf "Usage\n";
	@awk '{ \
			if ($$0 ~ /^.PHONY: [a-zA-Z\-\_0-9]+$$/) { \
				helpCommand = substr($$0, index($$0, ":") + 2); \
				if (helpMessage) { \
					printf "\033[36m%-20s\033[0m %s\n", \
						helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^[a-zA-Z\-\_0-9.]+:/) { \
				helpCommand = substr($$0, 0, index($$0, ":")); \
				if (helpMessage) { \
					printf "\033[36m%-20s\033[0m %s\n", \
						helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^##/) { \
				if (helpMessage) { \
					helpMessage = helpMessage"\n                     "substr($$0, 3); \
				} else { \
					helpMessage = substr($$0, 3); \
				} \
			} else { \
				if (helpMessage) { \
					print "\n                     "helpMessage"\n" \
				} \
				helpMessage = ""; \
			} \
		}' \
		$(MAKEFILE_LIST)

## ===== Miscellaneous =====

## Formattin Python scripts by Black.
format:
	@black .

##  Build MicroPython unix port by given version code
build-mpy:
	@for i in $(mpy_unix_build_versions); do \
		echo "[Build MicroPython unix port $$i]" ; \
		./bin/build_micropython.sh $$i ; \
	done

## Install MicroPython firmware for ESP32 based on variable `MICROPYTHON_FIRMWARE`.
install-firmware:
	@./bin/esp-install-firmware.sh $(MICROPYTHON_FIRMWARE) $(PORT)

## ===== Testing  (PC) =====

## Run all testing on PC
testing: $(py_testing_targets)

## Testing for Python 3.7.8
py-test:
	@echo "[Testing - Python]"
	@python -m tests.test_msgpack
	@python -m tests.test_mpy_env

## Testing for MicroPython (unix port)
mpy-unix-test:
	@for i in $(mpy_unix_build_versions); do \
		echo "[Testing - MicroPython (unix port) $$i]" ; \
		./bin/mpy_ver.sh $$i ; \
		micropython -m tests.test_msgpack ; \
		micropython -m tests.test_mpy_env ; \
	done

## MessagePack encode/decode validation
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

# Update m_mpfs_cmd.mk before execute `mpy_upload_targets`
ifndef MAKE_RESTARTS
ifneq ($(filter $(mpy_upload_targets),$(MAKECMDGOALS)),)
# Force update included makefile & reload them.
m_mpfs_cmd.mk: .FORCE_UPDATE
	@python -B -u ./tools/dump_mpfs_cmd.py
endif
endif

## ===== MicroPython (mpfshell) =====

## Enter mpfshell & connect to the micropython board.
mpy-open:
	@mpfshell --reset -c "open $(MPFSHELL_PORT)"

## List the files on the micropython board.
## $ make mpy-ls [path=</remote/path>]
mpy-ls:
	@if [ -z "$(path)" ]; then \
		$(call fn_mpfs, "open $(MPFSHELL_PORT);ls") ; \
	else \
		$(call fn_mpfs, "open $(MPFSHELL_PORT);cd $(path);ls") ; \
	fi

## Upload the local source to the micropython board.
## $ make mpy-upload-src [update=.]
mpy-upload-src:
	@if [ -z "$(update)" ]; then \
		$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_mk_src_dirs);$(mpy_put_src_files)") ; \
	else \
		$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_put_src_files)") ; \
	fi

## Clean the remote source on the micropython board.
mpy-clean-src:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_rm_src)")

## Upload the local tests to the micropython board.
## $ make mpy-upload-tests [update=.]
# 
mpy-upload-tests:
	@python -c "$$_pyc_0"
	@if [ -z "$(update)" ]; then \
        $(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_put_env);$(mpy_mk_tests_dirs);$(mpy_put_tests_files)") ; \
    else \
        $(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_put_env);$(mpy_put_tests_files)") ; \
    fi
	@echo "remove local 'env.json' & 'env.msgpack'" && rm ./env.json &&rm ./env.msgpack

## Clean the remote tests on the micropython board.
mpy-clean-tests:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_rm_env);$(mpy_rm_tests)")

## Upload examples to the micropython board.
## $ make mpy-upload-examples [update=.]
mpy-upload-examples:
	@if [ -z "$(update)" ]; then \
        $(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_mk_examples_dirs);$(mpy_put_examples_files)") ; \
    else \
        $(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_put_examples_files)") ; \
    fi

## Clean the remote examples on the micropython board.
mpy-clean-examples:
	@$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_rm_examples)")

## Run testing on multiple firware version on  ESP32.
mpy-testing-esp32:
	@python -c "$$_pyc_0"
	@for fw in $(mpy_esp32_build_versions); do \
		echo "[Testing - MicroPython (ESP32) $$fw]" ; \
		./bin/esp-install-firmware.sh $$fw $(PORT) ; \
		$(call fn_mpfs, "open $(MPFSHELL_PORT);$(mpy_upload_testing);$(mpy_exec_testing);$(mpy_clean_testing)") ; \
	done
	@echo "remove local 'env.json' & 'env.msgpack'" && rm ./env.json &&rm ./env.msgpack

## ===== Distribution =====

## Build source distribution.
sdist:
	@python setup.py sdist
	@rm -rf ./dist/*.tar.gz.orig
## Clean source distribution.
sdist-clean:
	@rm -rf ./dist ./*egg-info ./MANIFEST
## Upload distribution to PyPI.
upload-pypi:
	@twine upload --repository pypi dist/*
## Upload distribution to test PyPI.
upload-testpypi:
	@twine upload --repository testpypi dist/*

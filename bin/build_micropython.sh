#!/bin/sh
# 1. Build MicroPython unix port by given version code
# 2. Copy the executbales to "$HOME/.micropython/bin".
# 3. Createdsymbolic links into user binaries directory.
#
# You must set environment variable "MPY_PATH" as path of local MicroPython repository.
# The names of the executable copies corresponding to version 1.13 are "micropython113" and "mpy-cross113".
#

# Env : MPY_PATH
[ -z "$MPY_PATH" ] && { echo "You must set environment variable 'MPY_PATH' as path of local MicroPython repository." && exit; }
[ ! -d "$MPY_PATH" ] && { echo "'$MPY_PATH' is not exist." && exit; }

micropython_path="$MPY_PATH"
micropython_bin_path="$HOME/.micropython/bin"
mpy_cross_path="$micropython_path/mpy-cross"
unix_port_path="$micropython_path/ports/unix"

clean_build(){
    cd "$mpy_cross_path" && make V=1 clean 
    cd "$unix_port_path" && make  V=1 clean
    echo "clean the build."
}

build(){
    cd "$micropython_path"
    [ ! $(git tag -l "$1") ] && { echo "Invalid version." && exit; }

    version_code=$(echo "$1" | sed "s/[^0-9]*//g")
    micropython_executable="$micropython_bin_path/micropython$version_code"
    mpy_cross_executable="$micropython_bin_path/mpy-cross$version_code"

    clean_build
    git checkout "$1"
    cd "$mpy_cross_path" && make
    cp mpy-cross "$mpy_cross_executable"
    cd  "$unix_port_path" && make
    cp micropython "$micropython_executable"
    # Created symbolic links into user binaries directory
    user_bin_path=$(systemd-path user-binaries)
    ln -s -f "$micropython_executable" "$user_bin_path/micropython"
    echo "'$user_bin_path/micropython' references to '$micropython_executable' now."
    ln -s -f "$mpy_cross_executable" "$user_bin_path/mpy-cross"
    echo "'$user_bin_path/mpy-cross' references to '$mpy_cross_executable' now."
}

# arg1 : MicroPython version.
[ -z "$1" ] && { echo "1st argument must specify MicroPython version." && exit; }

mkdir -p "$micropython_bin_path"
build $1

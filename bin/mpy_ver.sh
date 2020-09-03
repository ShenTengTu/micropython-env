#!/bin/sh
# Change  MicroPython unix port version.

# arg1 : MicroPython version.
exit_msg="1st argument must specify MicroPython version."
[ -z "$1" ] && { echo "$exit_msg" && exit; }

# MicroPython binaries directory
micropython_bin_path="$HOME/.micropython/bin"
exit_msg="'$micropython_bin_path' is not exist. Please execute 'build_micropython.sh' first." 
[ ! -d "$micropython_bin_path" ] && { echo "$exit_msg" && exit; }

version_code=$(echo "$1" | sed "s/[^0-9]*//g")

# MicroPython executable path
micropython_executable="$micropython_bin_path/micropython$version_code"
exit_msg="'$micropython_executable' is not exist. Please execute 'build_micropython.sh' first." 
[ ! -f "$micropython_executable" ] && { echo "$exit_msg" && exit; }

# mpy-cross executable path
mpy_cross_executable="$micropython_bin_path/mpy-cross$version_code"
exit_msg="'$mpy_cross_executable' is not exist. Please execute 'build_micropython.sh' first." 
[ ! -f "$mpy_cross_executable" ] && { echo "$exit_msg" && exit; }

# Created symbolic links into user binaries directory
user_bin_path=$(systemd-path user-binaries)
ln -s -f "$micropython_executable" "$user_bin_path/micropython"
echo "'$user_bin_path/micropython' references to '$micropython_executable' now."
ln -s -f "$mpy_cross_executable" "$user_bin_path/mpy-cross"
echo "'$user_bin_path/mpy-cross' references to '$mpy_cross_executable' now."
micropython -c "import sys;print(sys.implementation)"
mpy-cross --version
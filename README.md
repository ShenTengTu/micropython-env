# micropython-env
Simple environment variable loader for MicroPython board.

The loader could load environment variables from the one of file format as below:
- [JSON] (default) : The file name is "env.json" (text mode).
- [MessagePack]: The file name is "env" or "env.msgpack" (binary mode).

# How to Use
```python
from mpy_env import load_env, get_env, put_env

# Loading `env.json` at once as default.
# You can invoke below function in `boot.py`
load_env()
# or
load_env(0)

# You can loading environment variables from MessagePack as below.
load_env(1)

# In `main.py` or the other,
# You can invoke below function to get environment variable.
get_env('key')

# You can invoke below function to set environment variable in-memory.
put_env('tuple', ('a', 1))
```

# Testing
Currentl testing environment:
- Python 3.7
- MicroPython unix port 1.12 ＆ 1.13
- MicroPython esp32 port 1.12＆ 1.13

Before tesing, you need to compile Micopython unix port executable first, see [offcial GitHub Wiki] to setup.

We use [mpfshell] to interactive with MicroPython board,  please install the latest release from PyPi.
```
pip install mpfshell
```

We use [offcial MessagePack package] to validate custom `msgpack` module, please install the latest release from PyPi.
```
pip install msgpack
```

Next, clone the repository to your local machine.
```
git clone https://github.com/ShenTengTu/micropython-env.git
cd micropython-env
```

You can execute the follow command to build muitiple versions of MicroPython unix port.
```
export MPY_PATH=<local_micropython_repo> && make build-mpy
```
> It will create symbolic links into user binaries directory after building.

To test on Python & MicroPython unix port,  execute the command as below.
```
make testing 
```
>  It will run testing on multiple MicroPython unix port versions.

To test on ESP32 board, execute the follow command.
```
make mpy-testing-esp32
```
>  It will run testing on multiple MicroPython esp32 port versions.

[JSON]: https://www.json.org/ 
[MessagePack]: https://msgpack.org/
[offcial GitHub Wiki]: https://github.com/micropython/micropython/wiki/Getting-Started
[mpfshell]: https://github.com/wendlers/mpfshell
[offcial MessagePack package]: https://github.com/msgpack/msgpack-python
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

[JSON]: https://www.json.org/ 
[MessagePack]: https://msgpack.org/
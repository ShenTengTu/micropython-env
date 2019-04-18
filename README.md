# micropython-env
Simple environment variable loader for MicroPython. The Loader read `env.json` on root path.

# How to Use
```python
from Env import Env # import Env class

Env.verbose = False # close verbose info

Env.load() # load env.json

Env.get('key') #  get environment variable

Env.put('tuple', ('a', 1)) # set environment variable
```
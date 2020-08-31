# Use custom package to dump MessagePack on Micropython (unix port)
from mpy_env.msgpack import serialize
import os
from . import DATA

here = "/".join([os.getenv("PWD")] + __file__.split("/")[:-1])
with open("/".join([here, "mpy.msgpack"]), "wb") as fp:
    fp.write(serialize(DATA))

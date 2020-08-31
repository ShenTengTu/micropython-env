# Use custom package to load MessagePack on Micropython (unix port)
from mpy_env.msgpack import deserialize
import os
from . import DATA, assertDictEqual

here = "/".join([os.getenv("PWD")] + __file__.split("/")[:-1])
with open("/".join([here, "mpy.msgpack"]), "rb") as fp:
    d = deserialize(fp.read())
assertDictEqual(d, DATA)

here = "/".join([os.getenv("PWD")] + __file__.split("/")[:-1])
with open("/".join([here, "official.msgpack"]), "rb") as fp:
    d = deserialize(fp.read())
assertDictEqual(d, DATA)

# Use official package to load MessagePack
import msgpack
from pathlib import Path
from . import DATA, assertDictEqual

with open(Path(__file__).parent.joinpath("official.msgpack"), "rb") as fp:
    d = msgpack.unpackb(fp.read(), strict_map_key=False)
assertDictEqual(d, DATA)

with open(Path(__file__).parent.joinpath("mpy.msgpack"), "rb") as fp:
    d = msgpack.unpackb(fp.read(), strict_map_key=False)
assertDictEqual(d, DATA)

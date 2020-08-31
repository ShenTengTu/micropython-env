# Use official package to dump MessagePack
import msgpack
from pathlib import Path
from . import DATA

with open(Path(__file__).parent.joinpath("official.msgpack"), "wb") as fp:
    fp.write(msgpack.packb(DATA))

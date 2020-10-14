import sys
from mpy_env.msgpack import serialize, deserialize

is_mpy = sys.implementation.name == "micropython"

## == Nil, Boolean == ##
assert deserialize(serialize(None)) == None
assert deserialize(serialize(True)) == True
assert deserialize(serialize(False)) == False
## == Binary == ##
b = bytearray(range(128))
x = deserialize(serialize(b))
assert type(x) is bytes
assert x == bytes(b)  # bin8
b = bytearray(list(range(256)) + list(range(128)))
assert deserialize(serialize(b)) == bytes(b)  # bin16
if not is_mpy:  # memory limit
    l = []
    for _ in range(257):
        l += list(range(256))
    b = bytearray(l)
    assert deserialize(serialize(b)) == bytes(b)  # bin32
    del l
del b
## == Float == ##
x = -3.14159265359
assert deserialize(serialize(0.25, single_float=True)) == 0.25  # float32
assert round(deserialize(serialize(x, single_float=True)), 6) == round(x, 6)  # float32
assert deserialize(serialize(x)) == x  # float64
x += -3.5e38
assert deserialize(serialize(x)) == x  # float64
del x
## == Integer == ##
assert deserialize(serialize(10)) == 10  # positive fixint
assert deserialize(serialize(-10)) == -10  # negative fixint
assert deserialize(serialize(200)) == 200  # uint8
assert deserialize(serialize(1000)) == 1000  # uint16
assert deserialize(serialize(70000)) == 70000  # uint32
try:
    assert deserialize(serialize(4300000000)) == 4300000000  # uint64
except OverflowError:
    print("Not support 'uint64' on this board (sys.maxsize: %d)" % sys.maxsize)
assert deserialize(serialize(-120)) == -120  # int8
assert deserialize(serialize(-30000)) == -30000  # int16
assert deserialize(serialize(-40000)) == -40000  # int32
try:
    assert deserialize(serialize(-2200000000)) == -2200000000  # int64
except OverflowError:
    print("Not support 'int64' on this board (sys.maxsize: %d)" % sys.maxsize)
## == String == ##
s = "1234567890"
assert deserialize(serialize(s)) == s  # fixstr
assert deserialize(serialize(s * 4)) == s * 4  # str8
assert deserialize(serialize(s * 30)) == s * 30  # str16
try:
    assert deserialize(serialize(s * 7000)) == s * 7000  # str32
except MemoryError:
    print("'str32' causes memory allocation failed on this board")
del s


## ========= ##
def assertListEqual(x, y):
    assert len(x) == len(y)
    for i in range(len(x)):
        item_x = x[i]
        item_y = y[i]
        type_x = type(item_x)
        type_y = type(item_y)
        assert type_x == type_y
        if type_x in (list, tuple):
            assertListEqual(item_x, item_y)
            continue
        if type_x is dict:
            assertDictEqual(item_x, item_y)
            continue
        assert item_x == item_y


def assertDictEqual(x, y):
    assert len(x) == len(y)
    for k_x, v_x in x.items():
        assert k_x in y
        v_y = y[k_x]
        type_x = type(v_x)
        type_y = type(v_y)
        assert type_x == type_y
        if type_x in (list, tuple):
            assertListEqual(v_x, v_y)
            continue
        if type_x is dict:
            assertDictEqual(v_x, v_y)
            continue
        assert v_x == v_y


## == Array == ##
l = (1, b"2", True, "3", False, 0.5, None)
assertListEqual(deserialize(serialize(l)), l)  # fixarray
l_a = l * 5
assertListEqual(deserialize(serialize(l_a)), l_a)  # array16
if not is_mpy:  # memory limit
    l_a = l_a * 1880
    assertListEqual(deserialize(serialize(l_a)), l_a)  # array32
    del l_a
del l
## == Map == ##
d = {2: None, b"10": 10, True: b"foo", "3": False, False: "bar", 0.5: True, None: 0.25}
assertDictEqual(deserialize(serialize(d)), d)  # fixmap
d = {}
for i in range(50):
    d[str(i)] = i
assertDictEqual(deserialize(serialize(d)), d)  # map16
if not is_mpy:  # memory limi
    d = {}
    for i in range(65600):
        d[str(i)] = i
    assertDictEqual(deserialize(serialize(d)), d)  # map32
del d
## == Nest == ##
l = (1, (b"2", (True, "3", {"1234567890": -70000}), False, 0.5), None)
assertListEqual(deserialize(serialize(l)), l)
d = {"bar": False, "wee": {b"2": 1000, True: l}, "foo": l}
assertDictEqual(deserialize(serialize(d)), d)
del l
del d


## == Ext : List == ##
t = [["2"], [False]]
assertListEqual(deserialize(serialize(t)), t)
t = [
    1,
    (
        b"2",
        [True, "3", {"1234567890": -70000, b"list": [1, b"2", [True], "3"]}],
        [False],
        0.5,
    ),
    None,
]
assertListEqual(deserialize(serialize(t)), t)
del t

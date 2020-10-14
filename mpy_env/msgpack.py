# MIT License
#
# Copyright (c) 2020 涂紳騰(Shen-Teng Tu)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# gist: https://gist.github.com/ShenTengTu/b33f3da7f6c2cbe605698c1759e0e230

import sys
import struct

__all__ = ["serialize", "deserialize"]

# 0x00 ~ 0x7f for application-specific type
_EXT_LIST = b"\x01"

_b_to_uint = lambda x: int.from_bytes(x, "big")

_two_comp = lambda x, y: (x - 2 ** y * (x >> (y - 1)))

_iter_encode = (
    lambda prefix, fmt_len, data: prefix
    + struct.pack(">%s" % fmt_len[0], fmt_len[1])
    + data
)

_number_encode = lambda prefix, fmt, f: prefix + struct.pack(">%s" % fmt, f)

_iterable_type = [list, tuple, dict]


def _app_ext_encode(obj):
    ## == Ext : List == ##
    if type(obj) is list:
        length = len(obj)
        data = b""
        for el in obj:
            data += serialize(el)
        if length <= 65535:
            ext_data = _iter_encode(b"", ("H", length), data)
        else:
            raise OverflowError("[Ext] List : The list  length out of  range (65535).")
        return (_EXT_LIST, ext_data)


def _app_ext_decode(ext_type, ext_data, _run):
    ## == Ext : List == ##
    if ext_type == _EXT_LIST:
        n_objs = _b_to_uint(ext_data[:2])
        objs_data = ext_data[2:]
        c = [None] * n_objs
        pointer = 0
        for i in range(n_objs):  # handle N objects
            el, p = _run(objs_data[pointer:], pointer)
            c[i] = el

            # If the element is sub list,
            # 'p' is actual length of bytes that represents the sub list.
            # The pointer need to update.
            if type(el) in _iterable_type:
                p += pointer
            pointer = p
        return c


def serialize(obj, single_float=False, ext_default=_app_ext_encode):
    """
    Simple function for MessagePack serialization.

    Support Extension type:
    - 0x01 : List
    """
    t = type(obj)
    ## == Nil, Boolean == ##
    if obj is None:
        return b"\xc0"
    if obj is False:
        return b"\xc2"
    if obj is True:
        return b"\xc3"
    ## == Binary == ##
    if t is bytearray:
        obj = bytes(obj)
        t = type(obj)
    if t is bytes:
        length = len(obj)
        if length <= 255:  # bin8
            return _iter_encode(b"\xc4", ("B", length), obj)
        if length <= 65535:  # bin16
            return _iter_encode(b"\xc5", ("H", length), obj)
        if length <= 4294967295:  # bin32
            return _iter_encode(b"\xc6", ("I", length), obj)
        raise OverflowError("The bytearray length is out of the range")
    ## == Float == ##
    if t is float:
        f32_max = (2 - 2 ** -23) * 2 ** 127
        f64_max = (2 - 2 ** -52) * 2 ** 1023
        if obj >= -f32_max and obj <= f32_max:  # float32
            if not single_float:  # float64
                return _number_encode(b"\xcb", "d", obj)
            return _number_encode(b"\xca", "f", obj)
        if obj >= -f64_max and obj <= f64_max:  # float64
            return _number_encode(b"\xcb", "d", obj)
        raise OverflowError("The float is out of the range")
    ## == Integer == ##
    if t is int:
        if obj >= -32 and obj < 0:  # negative fixint
            return _number_encode(b"", "b", obj)
        if obj >= 0 and obj <= 127:  # positive fixint
            return _number_encode(b"", "B", obj)
        if obj > 127 and obj <= 255:  # uint8
            return _number_encode(b"\xcc", "B", obj)
        if obj > 255 and obj <= 65535:  # unit16
            return _number_encode(b"\xcd", "H", obj)
        if obj > 65535 and obj <= 4294967295:  # unit32
            return _number_encode(b"\xce", "I", obj)
        if obj > 4294967295 and obj <= sys.maxsize:  # unit64
            return _number_encode(b"\xcf", "Q", obj)
        if obj >= -128 and obj < -32:  # int8
            return _number_encode(b"\xd0", "b", obj)
        if obj >= -32768 and obj < -128:  # int16
            return _number_encode(b"\xd1", "h", obj)
        if obj >= -2147483648 and obj < -32768:  # int32
            return _number_encode(b"\xd2", "i", obj)
        if obj >= ~sys.maxsize and obj < -2147483648:  # int64
            return _number_encode(b"\xd3", "q", obj)
        raise OverflowError(
            "The integer is out of the range ( ~sys.maxsize <= x <= sys.maxsize )"
        )
    ## == String == ##
    if t is str:
        length = len(obj)
        if length <= 31:  # fixstr	(101xxxxx)
            return _iter_encode(b"", ("B", 0xA0 | length), obj.encode("utf-8"))
        if length <= 255:  # str8
            return _iter_encode(b"\xd9", ("B", length), obj.encode("utf-8"))
        if length <= 65535:  # str16
            return _iter_encode(b"\xda", ("H", length), obj.encode("utf-8"))
        if length <= 4294967295:  # str32
            return _iter_encode(b"\xdb", ("I", length), obj.encode("utf-8"))
        raise OverflowError("The string length is out of the range")
    ## == Array == ##
    if t is tuple:
        length = len(obj)
        data = b""
        for el in obj:
            data += serialize(el)
        if length <= 15:  # fixarray (1001xxxx)
            return _iter_encode(b"", ("B", 0x90 | length), data)
        if length <= 65535:  # array16
            return _iter_encode(b"\xdc", ("H", length), data)
        if length <= 4294967295:  # array32
            return _iter_encode(b"\xdd", ("I", length), data)
        raise OverflowError("The array length is out of the range")
    ## == Map == ##
    if t is dict:
        length = len(obj)
        data = b""
        for k, v in obj.items():
            data += serialize(k)
            data += serialize(v)
        if length <= 15:  # fixmap	(1000xxxx)
            return _iter_encode(b"", ("B", 0x80 | length), data)
        if length <= 65535:  # map16
            return _iter_encode(b"\xde", ("H", length), data)
        if length <= 4294967295:  # map32
            return _iter_encode(b"\xdf", ("I", length), data)
        raise OverflowError("The array length is out of the range")

    ##### Extensions #####
    if callable(ext_default):
        ext_type, ext_data = ext_default(obj)
        length = len(ext_data)
        tp = ext_type + ext_data
        if length == 1:  # fixext 1
            return b"\xd4" + tp
        elif length == 2:  # fixext 2
            return b"\xd5" + tp
        elif length == 4:  # fixext 4
            return b"\xd6" + tp
        elif length == 8:  # fixext 8
            return b"\xd7" + tp
        elif length == 16:  # fixext 16
            return b"\xd8" + tp
        elif length <= 255:  # ext 8
            return _iter_encode(b"\xc7", ("B", length), tp)
        elif length <= 65535:  # ext 16
            return _iter_encode(b"\xc8", ("H", length), tp)
        elif length <= 4294967295:  # ext 32
            return _iter_encode(b"\xc9", ("I", length), tp)
        raise OverflowError("[Ext] : Data Length out of the extension range.")

    raise TypeError("The object type is unsupport.")


def deserialize(raw_data, ext_hook=_app_ext_decode):
    """
    Simple function for MessagePack de-serialization.

    Support Extension type:
    - 0x01 : List
    """

    def _array_decode(n_objs, objs_data):
        c = [None] * n_objs
        pointer = 0
        for i in range(n_objs):  # handle N objects
            el, p = _run(objs_data[pointer:], pointer)
            c[i] = el

            # If the element is sub list,
            # 'p' is actual length of bytes that represents the sub list.
            # The pointer need to update.
            if type(el) in _iterable_type:
                p += pointer
            pointer = p

        # 'pointer' is actual length of bytes that represents the list.
        return (tuple(c[i] for i in range(n_objs)), pointer + 1)

    def _map_decode(n_items, items_data):
        c = {}
        pointer = 0
        for _ in range(n_items):  # handle N items
            k, p_k = _run(items_data[pointer:], pointer)
            v, p_v = _run(items_data[p_k:], p_k)
            c[k] = v

            # If the element is sub list,
            # 'p_v' is actual length of bytes that represents the sub list.
            # The pointer need to update.
            if type(v) in _iterable_type:
                p_v += p_k
            pointer = p_v

        # 'pointer' is actual length of bytes that represents the list.
        return (c, pointer + 1)

    # 'pointer' is index of the next unprocess byte
    def _run(raw, pointer):
        prefix = raw[0:1]
        ## == Nil, Boolean == ##
        if prefix == b"\xc0":
            return (None, pointer + 1)
        if prefix == b"\xc2":
            return (False, pointer + 1)
        if prefix == b"\xc3":
            return (True, pointer + 1)
        ## == Binary == ##
        prefixs = b"\xc4\xc5\xc6"
        if prefix in prefixs:
            index = 2 ** prefixs.index(prefix)
            length = _b_to_uint(raw[1 : index + 1])
            return (
                raw[index + 1 : index + length + 1],
                pointer + 1 + index + length,
            )
        ## == Float == ##
        prefixs = b"\xca\xcb"
        if prefix in prefixs:
            length = 2 ** prefixs.index(prefix) * 4
            float_data = raw[1 : length + 1]
            if length == 4:
                return (
                    struct.unpack(">f", float_data)[0],
                    pointer + 1 + length,
                )
            if length == 8:
                return (
                    struct.unpack(">d", float_data)[0],
                    pointer + 1 + length,
                )
        ## == Integer == ##
        prefix_unit = _b_to_uint(prefix)
        if prefix_unit >= 0x00 and prefix_unit <= 0x7F:  # positive fixint
            return (prefix_unit, pointer + 1)
        if prefix_unit >= 0xE0 and prefix_unit <= 0xFF:  # negative fixint
            return (_two_comp(prefix_unit, 8), pointer + 1)
        prefixs = b"\xcc\xcd\xce\xcf"
        if prefix in prefixs:
            length = 2 ** prefixs.index(prefix)
            return (_b_to_uint(raw[1 : length + 1]), pointer + 1 + length)
        prefixs = b"\xd0\xd1\xd2\xd3"
        if prefix in prefixs:
            length = 2 ** prefixs.index(prefix)
            return (
                _two_comp(_b_to_uint(raw[1 : length + 1]), length * 8),
                pointer + 1 + length,
            )
        ## == String == ##
        if prefix_unit >= 0xA0 and prefix_unit <= 0xBF:  # fixstr
            length = ~0xA0 & prefix_unit
            return (raw[1 : length + 1].decode("utf-8"), pointer + 1 + length)
        prefixs = b"\xd9\xda\xdb"
        if prefix in prefixs:
            index = 2 ** prefixs.index(prefix)
            length = _b_to_uint(raw[1 : index + 1])
            return (
                raw[index + 1 : index + length + 1].decode("utf-8"),
                pointer + 1 + index + length,
            )
        ## == Array == ##
        if prefix_unit >= 0x90 and prefix_unit <= 0x9F:  # fixarray
            n_objs = ~0x90 & prefix_unit
            objs_data = raw[1:]  # The actual length is unknown
            return _array_decode(n_objs, objs_data)
        prefixs = b"\xdc\xdd"
        if prefix in prefixs:
            index = 2 * (prefixs.index(prefix) + 1)
            n_objs = _b_to_uint(raw[1 : index + 1])
            objs_data = raw[index + 1 :]  # The actual length is unknown
            return _array_decode(n_objs, objs_data)
        ## == Map == ##
        if prefix_unit >= 0x80 and prefix_unit <= 0x8F:  # fixmap
            n_items = ~0x80 & prefix_unit
            items_data = raw[1:]  # The actual length is unknown
            return _map_decode(n_items, items_data)
        prefixs = b"\xde\xdf"
        if prefix in prefixs:
            index = 2 * (prefixs.index(prefix) + 1)
            n_items = _b_to_uint(raw[1 : index + 1])
            items_data = raw[index + 1 :]  # The actual length is unknown
            return _map_decode(n_items, items_data)

        ##### Extensions #####
        if callable(ext_hook):
            prefixs = b"\xd4\xd5\xd6\xd7\xd8\xc7\xc8\xc9"
            if prefix in prefixs:
                index = prefixs.index(prefix)
                if index <= 4:
                    length = 2 ** index
                    ext_type = raw[1:2]
                    pointer = 2 + length
                    ext_data = raw[2:pointer]
                else:
                    x = 2 ** (index - 5) + 1
                    length = _b_to_uint(raw[1:x])
                    ext_type = raw[x : x + 1]
                    pointer = x + 1 + length
                    ext_data = raw[x + 1 : pointer]
                return (ext_hook(ext_type, ext_data, _run), pointer)

    obj, _ = _run(raw_data, 0)
    return obj

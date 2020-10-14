import sys
import os
from mpy_env import _Env, load_env, get_env, put_env

is_mpy = sys.implementation.name == "micropython"


def path_ioin(*args):
    return "/".join(args)


cwd = _Env._get_cwd()

## ==  _Env._select_exist_file(...) == ##
assert _Env._select_exist_file(path_ioin(cwd, "not.exist")) is None
if sys.platform == "linux":
    file_path = _Env._select_exist_file(
        path_ioin(cwd, "not.exist1"),
        path_ioin(cwd, "README.md"),
        path_ioin(cwd, "not.exist2"),
    )
    assert file_path == path_ioin(cwd, "README.md")
else:
    file_path = _Env._select_exist_file(
        path_ioin(cwd, "not.exist1"),
        path_ioin(cwd, "tests", "test_mpy_env.py"),
        path_ioin(cwd, "not.exist2"),
    )
    assert file_path == path_ioin(cwd, "tests", "test_mpy_env.py")


## ==  load_env(),  get_env() == ##
# if is_mpy : #and not sys.platform == "linux":
# See `_pyc_0` In Makefile
load_env(verbose=True)  # load 'env.json' at root
assert get_env("foo") == True
assert get_env("bar") == 1000
assert get_env("wee")[0] == 3.14159
assert get_env("ext_list")[0][0] == "2"
assert get_env("ext_list")[1][0] == False

# Force clean up _Env
if is_mpy:
    setattr(_Env, "__loaded", False)
    setattr(_Env, "__env", {})
else:
    setattr(_Env, "_Env__loaded", False)
    setattr(_Env, "_Env__env", {})

load_env(1, verbose=True)  # load 'env.msgpack' at root
assert get_env("foo") == True
assert get_env("bar") == 1000
obj = get_env("wee")
assert type(obj) is tuple
assert obj[0] == 3.14159
obj = get_env("ext_list")
assert type(obj) is list
assert type(obj[0]) is list
assert type(obj[1]) is list
assert obj[0][0] == "2"
assert obj[1][0] == False

## ==  put_env() == ##
put_env("platform", sys.platform)
assert get_env("platform") == sys.platform

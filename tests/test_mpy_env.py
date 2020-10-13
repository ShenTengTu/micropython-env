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
# In Makefile, the testing data is  {"foo": True, "bar": 1000, "wee": [3.14159]}
load_env(verbose=True)  # load 'env.json' at root
assert get_env("foo") == True
assert get_env("bar") == 1000
assert get_env("wee")[0] == 3.14159

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
assert get_env("wee")[0] == 3.14159

## ==  put_env() == ##
put_env("platform", sys.platform)
assert get_env("platform") == sys.platform

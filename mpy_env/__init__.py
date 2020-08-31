import os
import io
import json
from .msgpack import serialize, deserialize


class _Env:
    """Environment variable loader For MicroPython board.

    This class would load environment variables from the one of file format as below:
    - JSON (default) : The file name is "env.json"
    - MessagePack: The file name is "env" or "env.msgpack"
    """

    __loaded = False
    __env = {}
    verbose = False

    @staticmethod
    def _select_exist_file(path, *args):
        result = None
        for p in (path,) + args:
            try:
                result = p
                os.stat(result)
                break
            except OSError:
                result = None
        return result

    @classmethod
    def load_from_json(cls):
        if not cls.__loaded:
            cwd = os.getcwd()
            file_path = cls._select_exist_file(cwd + "/env.json")
            if file_path is None:
                if cls.verbose:
                    print("'env.josn' is not exist at root.")
                    return
            f = io.open(file_path, mode="r+", encoding="utf-8")
            env_dict = json.load(f)
            cls.__env.update(env_dict)
            f.close()
            cls.__loaded = True
            if cls.verbose:
                print("'%s' is loaded." % file_path)

    @classmethod
    def load_from_msgpack(cls):
        if not cls.__loaded:
            cwd = os.getcwd()
            file_path = cls._select_exist_file(cwd + "/env", cwd + "/env.msgpack")
            if file_path is None:
                if cls.verbose:
                    print("'env' or 'env.msgpack' is not exist at root.")
                    return
            f = io.open(file_path, mode="r+b")
            env_dict = deserialize(f.read())
            cls.__env.update(env_dict)
            f.close()
            cls.__loaded = True
            if cls.verbose:
                print("'%s' is loaded." % file_path)

    @classmethod
    def get(cls, key: str):
        return cls.__env.get(key)

    @classmethod
    def put(cls, key: str, obj):
        cls.__env[key] = obj


def load_env(f_type=0, verbose=False):
    """Loading environment variables from the file at root.
    """
    _Env.verbose = verbose
    if f_type == 0:
        return _Env.load_from_json()
    if f_type == 1:
        return _Env.load_from_msgpack()


def get_env(key: str):
    """Get the loaded environment variable.
    """
    return _Env.get(key)


def put_env(key: str, obj):
    """Set an environment variable
    """
    _Env.put(key, obj)

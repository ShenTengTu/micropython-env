from mpy_env import get_env

print(get_env("foo"))  # True
print(get_env("bar"))  # 1000
print(get_env("wee"))  # [3.14159]

from mpy_env import load_env, put_env

# Loading `env.json` at once as default.
# if `verbose` is true, the loader will print debug messages
load_env(verbose=True)

# Add environment variable in-memory
put_env("tuple", ("a", 1))

import uos
import uio
import ujson

class Env():
    '''
    Environment variable loader. Load `env.json` at root .
    '''
    __loaded = False
    __env = {}
    verbose = True

    @staticmethod
    def load():
        ''' load environment variable from env.json '''
        if Env.__loaded is False:
            try:
                env = uio.open(uos.getcwd() + 'env.json', mode='r', encoding="utf-8")
                env_dict = ujson.load(env)
                Env.__env.update(env_dict)
                Env.__loaded = True
            except OSError:
                if Env.verbose is True:
                    print('No env.json in root.')

    @staticmethod
    def get(key: str):
        ''' get environment variable by key '''
        return Env.__env.get(key)

    @staticmethod
    def put(key: str, value):
        ''' set environment variable by key '''
        Env.__env[key] = value

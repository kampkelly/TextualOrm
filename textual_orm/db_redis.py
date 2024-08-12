import redis

REDIS_PATH = "textualorm"


def redis_setup(host: str, port: int):
    r = redis.Redis(host=host, port=port)
    r.ping()
    return r

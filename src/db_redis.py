import redis

REDIS_PATH = "orm"


def redis_setup(host: str, port: int):
    r = redis.Redis(host=host, port=port)
    return r

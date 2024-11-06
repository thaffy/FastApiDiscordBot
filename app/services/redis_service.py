from redis import Redis


class RedisService:
    def __init__(self, redis: Redis = None):
        self.redis = redis.client()

    async def write(self, key, value):
        return self.redis.set(key, value)

    async def read(self, key):
        return self.redis.get(key)

    async def delete(self, key):
        return self.redis.delete(key)

    async def invalidate(self):
        return self.redis
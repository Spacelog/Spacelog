import os
import redis

class RedisMiddleware(object):
    """
    Add a redis object to every request
    """
    def process_request(self, request):
        request.redis_conn = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))

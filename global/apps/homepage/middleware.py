import os
import redis
from django.utils.deprecation import MiddlewareMixin

class RedisMiddleware(MiddlewareMixin):
    """
    Add a redis object to every request
    """
    def process_request(self, request):
        request.redis_conn = redis.from_url(
            os.environ.get("REDIS_URL", "redis://localhost:6379"),
            decode_responses=True
        )

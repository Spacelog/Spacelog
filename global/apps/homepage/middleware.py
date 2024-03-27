from django.utils.deprecation import MiddlewareMixin
from backend.util import redis_connection

class RedisMiddleware(MiddlewareMixin):
    """
    Add a redis object to every request
    """
    def process_request(self, request):
        request.redis_conn = redis_connection

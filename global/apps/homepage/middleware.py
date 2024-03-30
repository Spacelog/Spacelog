from backend.util import redis_connection

class RedisMiddleware(object):
    """
    Add a redis object to every request
    """
    def process_request(self, request):
        request.redis_conn = redis_connection

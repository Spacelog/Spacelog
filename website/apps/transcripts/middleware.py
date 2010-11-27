import redis
from backend.api import Mission

class MissionMiddleware(object):

    def process_request(self, request):
        request.redis_conn = redis.Redis()
        request.mission = Mission(request.redis_conn, "a13")


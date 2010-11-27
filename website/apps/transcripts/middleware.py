import redis
from backend.api import Mission

class MissionMiddleware(object):

    def process_request(self, request):
        request.redis_conn = redis.Redis()
        # Get the mission subdomain
        subdomain = request.META['HTTP_HOST'].split(".")[0]
        mission_name = request.redis_conn.get("subdomain:%s" % subdomain) or "a13"
        request.mission = Mission(request.redis_conn, mission_name)


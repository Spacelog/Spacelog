import redis
from django.http import HttpResponse
from django.shortcuts import render_to_response
from backend.api import Mission

class MissionMiddleware(object):
    """
    Adds a mission and redis object into every request.
    """
    def process_request(self, request):
        request.redis_conn = redis.Redis()
        # Get the mission subdomain
        subdomain = request.META['HTTP_HOST'].split(".")[0]
        if not request.holding:
            mission_name = request.redis_conn.get("subdomain:%s" % subdomain) or "a13"
            request.mission = Mission(request.redis_conn, mission_name)

class HoldingMiddleware(object):
    """
    Shows a holding page if we're in the middle of an upgrade.
    """
    def process_request(self, request):
        redis_conn = redis.Redis()
        if redis_conn.get("hold"):
            if request.path.startswith("/assets"):
                request.holding = True
            else:
                return render_to_response("holding.html", {})
        else:
            request.holding = False


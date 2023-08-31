import os
import redis
from django.shortcuts import render_to_response
from django.template import RequestContext
from backend.api import Mission
from transcripts.templatetags.missiontime import component_suppression

class MissionMiddleware(object):
    """
    Adds a mission and redis object into every request.
    """
    def process_request(self, request):
        request.redis_conn = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
        # Get the current database
        # request.redis_conn.select(int(request.redis_conn.get("live_database") or 0))
        # Get the mission subdomain
        subdomain = request.get_host().split(".")[0]
        if not request.holding:
            mission_name = request.redis_conn.get("subdomain:%s" % subdomain) or "a13"
            request.mission = Mission(request.redis_conn, mission_name)
            if request.mission.copy.get('component_suppression', None):
                component_suppression.leading = request.mission.copy['component_suppression'].get('leading', None)                
                component_suppression.trailing = request.mission.copy['component_suppression'].get('trailing', None)
            else:
                component_suppression.leading = None
                component_suppression.trailing = None

class HoldingMiddleware(object):
    """
    Shows a holding page if we're in the middle of an upgrade.
    """
    def process_request(self, request):
        redis_conn = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
        # Get the current database
        # redis_conn.select(int(redis_conn.get("live_database") or 0))
        if redis_conn.get("hold"):
            if request.path.startswith("/assets"):
                request.holding = True
            else:
                response = render_to_response(
                    "holding.html",
                    {},
                    RequestContext(request),
                )
                response.status_code = 503
                return response
        else:
            request.holding = False


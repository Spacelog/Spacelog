import os
import redis
from django.shortcuts import render_to_response
from django.template import RequestContext
from backend.api import Mission
from transcripts.templatetags.missiontime import component_suppression

class RedisMiddleware(object):
    """
    Add a redis object to every request
    """
    def process_request(self, request):
        request.redis_conn = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))

class MissionMiddleware(object):
    """
    Adds a mission object into every request.
    """
    def process_request(self, request):
        # Get the mission subdomain
        subdomain = request.get_host().split(".")[0]

        mission_name = request.redis_conn.get("subdomain:%s" % subdomain) or "a13"
        request.mission = Mission(request.redis_conn, mission_name)
        if request.mission.copy.get('component_suppression', None):
            component_suppression.leading = request.mission.copy['component_suppression'].get('leading', None)
            component_suppression.trailing = request.mission.copy['component_suppression'].get('trailing', None)
        else:
            component_suppression.leading = None
            component_suppression.trailing = None

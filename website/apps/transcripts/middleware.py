from django.template import RequestContext
from backend.api import Mission
from backend.util import redis_connection
from transcripts.templatetags.missiontime import component_suppression
from django.utils.deprecation import MiddlewareMixin

class RedisMiddleware(MiddlewareMixin):
    """
    Add a redis object to every request
    """
    def process_request(self, request):
        request.redis_conn = redis_connection

class MissionMiddleware(MiddlewareMixin):
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

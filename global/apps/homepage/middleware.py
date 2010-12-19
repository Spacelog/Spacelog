import redis
from django.shortcuts import render_to_response
from django.template import RequestContext

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
                response = render_to_response(
                    "holding.html",
                    {},
                    RequestContext(request),
                )
                response.status_code = 503
                return response
        else:
            request.holding = False


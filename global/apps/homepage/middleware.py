import redis
from django.http import HttpResponse
from django.shortcuts import render_to_response

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


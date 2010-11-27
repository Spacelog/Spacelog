from django.shortcuts import render_to_response
from backend.api import Mission
import redis

def homepage(request):
    missions = list(Mission.Query(redis.Redis()))
    return render_to_response(
        'homepage/homepage.html',
        {
            'missions': missions
        },
    )
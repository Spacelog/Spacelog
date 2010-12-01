from django.shortcuts import render_to_response
from django.template import RequestContext
from backend.api import Mission
import redis

def homepage(request):
    missions = [
        mission for mission in list(Mission.Query(redis.Redis()))
        if not mission.incomplete
    ]
    missions_coming_soon = [
        {
            'name': 'g7',
            'coming_soon': True,
            'title': 'Gemini 7',
            'description': 'One half of the first orbital rendezvous.'
        },
        {
            'name': 'a8',
            'coming_soon': True,
            'title': 'Apollo 8',
            'description': 'The first human space flight to leave Earth orbit.'
        },
    ]
    return render_to_response(
        'homepage/homepage.html',
        {
            'missions': missions,
            'missions_coming_soon': missions_coming_soon
        },
        context_instance = RequestContext(request),
    )

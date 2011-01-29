from django.shortcuts import render_to_response
from django.template import RequestContext
from backend.api import Mission

def homepage(request):
    missions = [
        mission for mission in list(Mission.Query(request.redis_conn))
        if not mission.incomplete
    ]
    missions_coming_soon = [
        mission for mission in list(Mission.Query(request.redis_conn))
        if mission.incomplete
    ]
    return render_to_response(
        'homepage/homepage.html',
        {
            'missions': missions,
            'missions_coming_soon': missions_coming_soon
        },
        context_instance = RequestContext(request),
    )

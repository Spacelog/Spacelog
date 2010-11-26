from django.shortcuts import render_to_response
import redis
from backend.api import Character

def people(request):
    redis_conn = redis.Redis()
    astronauts = list(Character.Query( redis_conn, 'a13' ).role( 'astronaut' ))
    return render_to_response(
        'people/people.html',
        {
            'people': [
                {
                    'name': 'Flight Crew',
                    'members': astronauts,
                    'expanded_view': True
                },
                {
                    'name': 'Mission Control',
                    'members': astronauts[:2],
                    'expanded_view': False
                }
            ],
        },
    )
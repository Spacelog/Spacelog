from django.http import Http404
from django.shortcuts import render_to_response
import redis
from backend.api import Character

def people(request, role=None):
    redis_conn = redis.Redis()
    if role:
        people = [
            {
                'name': role,
                'members': list( Character.Query( redis_conn, 'a13' ).role( role ) ),
            }
        ]
    else:
        people = [
            {
                'name': 'Flight Crew',
                'members': list(Character.Query( redis_conn, 'a13' ).role( 'astronaut' )),
                'view': 'full'
            },
            {
                'name': 'Mission Control',
                'members': list(Character.Query( redis_conn, 'a13' ).role( 'mission-ops-title' )),
                'view': 'simple'
            }
        ]
    
    # 404 if we have no content
    if 1 == len(people) and 0 == len(people[0]['members']):
        raise Http404( "No people were found" )
    return render_to_response(
        'people/people.html',
        {
            'role':   role,
            'people': people,
        },
    )
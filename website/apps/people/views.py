from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
import redis
from backend.api import Character

def people(request, role=None):
    
    character_query = Character.Query(request.redis_conn, request.mission.name)

    if role:
        people = [
            {
                'name': role,
                'members': list(character_query.role(role)),
            }
        ]
    else:
        people = [
            {
                'name': 'Flight Crew',
                'members': list(character_query.role('astronaut')),
                'view': 'full'
            },
            {
                'name': 'Mission Control',
                'members': list(character_query.role('mission-ops-title')),
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
        context_instance = RequestContext(request),
    )

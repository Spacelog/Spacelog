from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from backend.api import Character

def people(request, role=None):
    
    character_query = Character.Query(request.redis_conn, request.mission.name)
    character_ordering = list(request.redis_conn.lrange("character-ordering:%s" % request.mission.name, 0, -1))
    sort_characters = lambda l: sorted(
        list(l),
        key=lambda x: character_ordering.index(x.identifier) if x.identifier in character_ordering else 100
    )

    if role:
        people = [
            {
                'name': role,
                'members': sort_characters(character_query.role(role)),
            }
        ]
        more_people = False
    else:
        all_people = sort_characters(character_query)
        astronauts = list(character_query.role('astronaut'))
        ops = sort_characters(character_query.role('mission-ops-title'))
        people = [
            {
                'name': 'Flight Crew',
                'members': astronauts,
                'view': 'full'
            },
            {
                'name': 'Mission Control',
                'members': ops,
                'view': 'simple'
            }
        ]
        more_people = len(list(character_query.role('mission-ops')))
    
    # 404 if we have no content
    if 1 == len(people) and 0 == len(people[0]['members']):
        raise Http404( "No people were found" )
    return render_to_response(
        'people/people.html',
        {
            'role':   role,
            'people': people,
            'more_people': more_people,
        },
        context_instance = RequestContext(request),
    )

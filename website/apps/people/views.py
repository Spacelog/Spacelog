from django.http import Http404
from django.views.generic import TemplateView
from common.views import MemorialMixin
from backend.api import Character

def mission_people(request, role=None):
    character_query = Character.Query(request.redis_conn, request.mission.name)
    character_ordering = [
        identifier
        for identifier in
        list(request.redis_conn.lrange("character-ordering:%s" % request.mission.name, 0, -1))
    ]
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

    return people, more_people


class PeopleView(TemplateView, MemorialMixin):
    template_name = 'people/people.html'

    def get_context_data(self, role=None, **kwargs):
        people, more_people = mission_people(self.request, role)

        # 404 if we have no content
        if 1 == len(people) and 0 == len(people[0]['members']):
            raise Http404( "No people were found" )

        return {
            'role': role,
            'people': people,
            'more_people': more_people,
        }

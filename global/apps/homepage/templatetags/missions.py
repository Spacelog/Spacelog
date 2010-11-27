from django.template import Library
from django.conf import settings

register = Library()

@register.filter
def featured(missions, featured=True):
    if featured != True:
        featured = (featured.lower() == 'true')
    return [ mission for mission in missions if mission.featured == featured ]

@register.filter
def mission_url(mission):
    return u"http://%s.%s/" % (mission, settings.PROJECT_DOMAIN)

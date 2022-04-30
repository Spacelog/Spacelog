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
    if isinstance(mission, basestring):
        return u"//%s.%s/" % (mission, settings.PROJECT_DOMAIN)
    else:
        if mission.subdomain is not None:
            return u"//%s.%s/" % (mission.subdomain, settings.PROJECT_DOMAIN)
        else:
            return u"//%s.%s/" % (mission.name, settings.PROJECT_DOMAIN)

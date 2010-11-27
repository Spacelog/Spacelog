from django.template import Library

register = Library()

@register.filter
def featured(missions, featured=True):
    if featured != True:
        featured = (featured.lower() == 'true')
    return [ mission for mission in missions if mission.featured == featured ]

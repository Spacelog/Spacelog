from django.template import Library
from django.core.urlresolvers import reverse

register = Library()

def timestamp_components(seconds):
    "Takes a timestamp in seconds and returns a tuple of days, hours, minutes and seconds"
    days = seconds // 86400
    hours = seconds % 86400 // 3600
    minutes = seconds % 3600 // 60
    seconds = seconds % 60
    return (days, hours, minutes, seconds)

def mission_time(seconds, separator):
    """
    Takes a timestamp and a separator and returns a mission time string
    e.g. Passing in 63 seconds and ':' would return '00:00:01:03'
    """
    mission_time = separator.join([ '%02d' % x for x in timestamp_components(abs(seconds)) ])
    if seconds < 0:
        mission_time = '-%s' % mission_time
    return mission_time

@register.filter
def mission_time_format(seconds):
    return mission_time(seconds, ' ')

@register.simple_tag
def timestamp_to_url(seconds):
    return reverse("view_page", kwargs={"timestamp":mission_time(seconds, ':')})

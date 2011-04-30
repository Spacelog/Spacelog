from django.template import Library
from django.core.urlresolvers import reverse
from backend.util import timestamp_to_seconds

from templatetag_sugar.register import tag
from templatetag_sugar.parser import Variable, Optional


import threading

register = Library()

component_suppression = threading.local()
component_suppression.leading = None
component_suppression.trailing = None # must be negative to trim!

def timestamp_components(seconds, enable_suppression=False):
    # FIXME: this is almost identical to backend.util.seconds_to_timestamp, so
    # refactor
    "Takes a timestamp in seconds and returns a tuple of days, hours, minutes and seconds"
    # FIXME: really nasty thread-local to suppress different ends
    days = seconds // 86400
    hours = seconds % 86400 // 3600
    minutes = seconds % 3600 // 60
    seconds = seconds % 60
    if enable_suppression:
        return (days, hours, minutes, seconds)[component_suppression.leading:component_suppression.trailing]
    else:
        return (days, hours, minutes, seconds)

def mission_time(seconds, separator=':', enable_suppression=False):
    """
    Takes a timestamp and a separator and returns a mission time string
    e.g. Passing in 63 seconds and ':' would return '00:00:01:03'.
    """
    if isinstance(seconds, basestring) and separator in seconds:
        return seconds
    mission_time = separator.join([ '%02d' % x for x in timestamp_components(abs(seconds), enable_suppression) ])
    if seconds < 0:
        mission_time = '-%s' % mission_time
    return mission_time

@register.filter
def mission_time_format(seconds):
    return mission_time(seconds, ' ', True)

@tag(register, [Variable(), Optional([Variable()])])
def timestamp_to_url(context, seconds, anchor=None):
    url_args = {
        "start": mission_time(seconds)
    }
    
    # Split transcript name from [mission]/[transcript]
    transcript = context['transcript_name'].split('/')[1]
    if context['transcript_name'] != context['mission_main_transcript']:
        url_args["transcript"] = transcript
    
    # Render the URL
    url = reverse("view_page", kwargs=url_args)
    if anchor:
        url = '%s#log-line-%s' % (url, anchor)
    return url

@tag(register, [Variable(), Optional([Variable()])])
def selection_url(context, start_seconds, end_seconds=None):
    url_args = {
        "start": mission_time(start_seconds)
    }
    if end_seconds:
        url_args["end"] = mission_time(end_seconds)
    
    # Split transcript name from [mission]/[transcript]
    transcript = context['transcript_name'].split('/')[1]
    if context['transcript_name'] != context['mission_main_transcript']:
        url_args["transcript"] = transcript
    
    # Render the URL
    url = reverse("view_range", kwargs=url_args)
    if isinstance(start_seconds, basestring):
        start_seconds = timestamp_to_seconds(start_seconds)
    return '%s#log-line-%i' % ( url, start_seconds )

from django.template import Library
from django.core.urlresolvers import reverse
from templatetag_sugar.register import tag
from templatetag_sugar.parser import Variable, Optional
from backend.util import timestamp_to_seconds

register = Library()

def timestamp_components(seconds):
    # FIXME: this is almost identical to backend.util.seconds_to_timestamp, so
    # refactor
    "Takes a timestamp in seconds and returns a tuple of days, hours, minutes and seconds"
    days = seconds // 86400
    hours = seconds % 86400 // 3600
    minutes = seconds % 3600 // 60
    seconds = seconds % 60
    return (days, hours, minutes, seconds)

def mission_time(seconds, separator=':'):
    """
    Takes a timestamp and a separator and returns a mission time string
    e.g. Passing in 63 seconds and ':' would return '00:00:01:03'
    """
    if isinstance(seconds, basestring) and separator in seconds:
        return seconds
    mission_time = separator.join([ '%02d' % x for x in timestamp_components(abs(seconds)) ])
    if seconds < 0:
        mission_time = '-%s' % mission_time
    return mission_time

@register.filter
def mission_time_format(seconds):
    return mission_time(seconds, ' ')

@tag(register, [Variable(), Optional([Variable(), Optional([Variable()])])])
def timestamp_to_url(context, seconds, anchor=None, transcript=None):
    # Construct the kwargs for the reverse lookup
    kwargs = {
        "start": mission_time(seconds),
    }
    if transcript and transcript != context['request'].mission.main_transcript:
        kwargs['transcript'] = transcript.split("/")[-1]
    # Go there
    url = reverse("view_page", kwargs=kwargs)
    if anchor:
        url = '%s#log-line-%s' % (url, anchor)
    return url

@register.simple_tag
def selection_url(start_seconds, end_seconds=None):
    if end_seconds is None:
        url = reverse("view_range", kwargs={"start": mission_time(start_seconds)})
    else:
        url = reverse("view_range", kwargs={"start": mission_time(start_seconds), "end": mission_time(end_seconds)})
    if isinstance(start_seconds, basestring):
        start_seconds = timestamp_to_seconds(start_seconds)
    return '%s#log-line-%i' % ( url, start_seconds )

import re
from django.template import Library
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from transcripts.templatetags.missiontime import selection_url

register = Library()

@register.filter
def linkify(text):
    text = re.sub(
        r"\[time:([\d:]+) ([^\]]+)\]",
        lambda m: "<a href='%s'>%s</a>" % (selection_url(int(m.group(1))), m.group(2)),
        text,
    )
    return mark_safe(text)

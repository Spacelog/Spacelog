import re
from django.template import Library
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from backend.api import Glossary
from backend.util import timestamp_to_seconds
from transcripts.templatetags.missiontime import timestamp_to_url

register = Library()

def glossary_link(match, request):
    # Try to look up the definition
    if request:
        try:
            gitem = Glossary(request.redis_conn, request.mission.name, match.group(1))
        except ValueError:
            title = ""
        else:
            title = gitem.description
    else:
        title = ""
    return "<a href='%s#%s'><abbr title='%s'>%s</abbr></a>" % (
        reverse("glossary"),
        slugify(match.group(1)),
        title,
        match.group(2),
    )

@register.filter
def linkify(text, request=None):
    # Typographize double quotes
    text = re.sub(r'"([^"]+)"', r'&ldquo;\1&rdquo;', text)
    text = text.replace("'", "&apos;").replace('...', '&hellip;')
    # Time links
    text = re.sub(
        r"\[time:([\d:]+) ([^\]]+)\]",
        lambda m: "<a href='%s'>%s</a>" % (
            timestamp_to_url(m.group(1), anchor="closest"),
            m.group(2)
        ),
        text,
    )
    # Glossary links
    text = re.sub(
        r"\[glossary:([^]]+) (\1)\]",
        lambda m: glossary_link(m, request),
        text,
    )
    # Dashing through the text, with a one-space open sleigh
    text = text.replace("- -", "&mdash;").replace(" - ", "&mdash;").replace("--", "&mdash;")
    return mark_safe(text)


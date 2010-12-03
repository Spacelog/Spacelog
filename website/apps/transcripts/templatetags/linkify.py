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
            more_information = True
        else:
            title = gitem.description
            more_information = bool(gitem.extended_description)
            tag = 'abbr' if gitem.type == 'abbreviation' else 'i'
    else:
        title = ""
        more_information = True

    term = match.group(2)

    if title:
        term = "<%(tag)s title='%(title)s'>%(text)s</%(tag)s>" % {
                    "tag":   tag,
                    "title": title,
                    "text":  match.group(1),
                }

    if more_information:
        return "<a href='%s#%s'>%s</a>" % (
            reverse("glossary"),
            slugify(match.group(1)),
            term,
        )
    else:
        return term

@register.filter
def linkify(text, request=None):
    # Typographize double quotes
    text = re.sub(r'"([^"]+)"', r'&ldquo;\1&rdquo;', text)
    text = text.replace('...', '&hellip;')
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


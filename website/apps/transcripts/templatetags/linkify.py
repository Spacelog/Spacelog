import re
from django.template import Library
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from backend.api import Glossary
from backend.util import timestamp_to_seconds
from .missiontime import timestamp_to_url

register = Library()

@register.simple_tag(takes_context=True)
def original_link(context, transcript, page):
    url_args = {
        'page': page,
    }
    if transcript != context['request'].mission.main_transcript:
        # Split transcript name from [mission]/[transcript]
        url_args["transcript"] = transcript.split('/')[1]
    
    return reverse("original", kwargs=url_args)


def glossary_link(match, request):
    # Try to look up the definition
    gitem = None
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

    try:
        # full syntax [glossary:term|display]
        display = match.group(2)
    except IndexError:
        # abbreviated syntax [glossary:term]
        display = match.group(1)

    if title:
        display = u"<%(tag)s class='jargon' title='%(title)s'>%(text)s</%(tag)s>" % {
            "tag":   tag,
            "title": title,
            "text":  display,
        }

    if more_information:
        if gitem is not None:
            return u"<a href='%s#%s'>%s</a>" % (
                reverse("glossary"),
                gitem.slug,
                display,
            )
        else:
            return u"<a href='%s#%s'>%s</a>" % (
                reverse("glossary"),
                slugify(match.group(1)),
                display,
            )
    else:
        return display

def time_link(match):
    try:
        # full syntax [time:time|display]
        return "<a href='%s'>%s</a>" % (
            timestamp_to_url({}, match.group(1), anchor="closest"),
            match.group(2)
        )
    except:
        # abbreviated syntax [time:time]
        return "<a href='%s'>%s</a>" % (
            timestamp_to_url({}, match.group(1), anchor="closest"),
            match.group(1)
        )

@register.filter
def linkify(text, request=None):
    # Typographize double quotes
    text = re.sub(r'"([^"]+)"', r'&ldquo;\1&rdquo;', text)
    text = text.replace('...', '&hellip;')
    
    link_types = {
        'time': time_link,
        'glossary': lambda m: glossary_link(m, request),
    }
    
    for link_type, link_maker in link_types.items():
        # first, the "full" version
        text = re.sub(
            r"\[%s:([^]]+)\|([^]]+)\]" % link_type,
            link_maker,
            text,
        )
        # Then the abbreviated syntax
        text = re.sub(
            r"\[%s:([^]]+)\]" % link_type,
            link_maker,
            text,
        )

    # Dashing through the text, with a one-space open sleigh
    text = text.replace("- -", "&mdash;").replace(" - ", "&mdash;").replace("--", "&mdash;")
    return mark_safe(text)

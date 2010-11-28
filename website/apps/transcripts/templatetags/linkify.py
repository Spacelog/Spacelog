import re
from django.template import Library
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from transcripts.templatetags.missiontime import selection_url

register = Library()

@register.filter
def linkify(text):
    # Time links
    text = re.sub(
        r"\[time:([\d:]+) ([^\]]+)\]",
        lambda m: "<a href='%s'>%s</a>" % (selection_url(m.group(1)), m.group(2)),
        text,
    )
    # Glossary links
    text = re.sub(
        r"\[glossary:(\w+) ([^\]]+)\]",
        lambda m: "<a href='%s#%s'>%s</a>" % (reverse("glossary"), m.group(1).upper(), m.group(2)),
        text,
    )
    # Typographize double quotes
    text = re.sub(
        r'"([^"]+)"', r'&ldquo;\1&rdquo;', text)
    # Dashing through the text, with a one-space open sleigh
    text = text.replace("- -", "&mdash;").replace(" - ", "&mdash;")
    return mark_safe(text)

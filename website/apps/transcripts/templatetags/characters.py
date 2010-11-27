from django.template import Library
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

register = Library()

@register.simple_tag
def avatar_and_name(speaker, timestamp=None):

    if timestamp:
        current_speaker = speaker.current_shift(timestamp)
    else:
        current_speaker = speaker

    detail = """
      <img src='%(avatar)s' alt='' width='48' height='48'>
      <span>%(short_name)s</span>
    """ % {"avatar": current_speaker.avatar, "short_name": current_speaker.short_name}

    url = None
    if current_speaker.role == 'mission-ops':
        url = '%s#%s' % (reverse("people", kwargs={"role": current_speaker.role}), slugify(current_speaker.short_name))
    elif current_speaker.role == 'astronaut' or current_speaker.role == 'mission-ops-title':
        url = '%s#%s' % (reverse("people"), slugify(current_speaker.short_name))

    if url:
        return "<a href='%s'>%s</a>" % (url, detail)
    else:
        return detail

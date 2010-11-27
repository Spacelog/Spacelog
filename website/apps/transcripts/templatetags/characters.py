from django.template import Library
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

register = Library()

@register.simple_tag
def avatar_and_name(speaker):
    detail = """
      <img src='%(avatar)s' alt='%(short_name)s' width='48' height='48'>
      <span>%(short_name)s</span>
    """ % {"avatar": speaker.avatar, "short_name": speaker.short_name}

    url = None
    if speaker.role == 'mission-ops':
        url = '%s#%s' % (reverse("people", kwargs={"role": speaker.role}), slugify(speaker.short_name))
    elif speaker.role == 'astronaut' or speaker.role == 'mission-ops-title':
        url = '%s#%s' % (reverse("people"), slugify(speaker.short_name))

    if url:
        return "<a href='%s'>%s</a>" % (url, detail)
    else:
        return detail

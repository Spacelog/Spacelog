from django.template import Library
from django.core.urlresolvers import reverse
from django.conf import settings

register = Library()

@register.simple_tag
def avatar_and_name(speaker, mission_name, timestamp=None):

    if timestamp is not None:
        current_speaker = speaker.current_shift(timestamp)
    else:
        current_speaker = speaker
    
    short_name_lang = ''
    if current_speaker.short_name_lang:
        short_name_lang = " lang='%s'"  % current_speaker.short_name_lang 
    
    detail = """
      <img src='%(MISSIONS_STATIC_URL)s%(mission_name)s/images/avatars/%(avatar)s' alt='' width='48' height='48'>
      <span%(short_name_lang)s>%(short_name)s</span>
    """ % {
        "avatar": current_speaker.avatar,
        "short_name": current_speaker.short_name,
        "short_name_lang": short_name_lang,
        "mission_name": mission_name,
        "MISSIONS_STATIC_URL": settings.MISSIONS_STATIC_URL,
    }

    url = None
    if current_speaker.role == 'mission-ops':
        url = '%s#%s' % (reverse("people", kwargs={"role": current_speaker.role}), current_speaker.slug)
    elif current_speaker.role == 'astronaut' or current_speaker.role == 'mission-ops-title':
        url = '%s#%s' % (reverse("people"), current_speaker.slug)

    if url:
        return "<a href='%s'>%s</a>" % (url, detail)
    else:
        return detail

@register.simple_tag
def avatar(speaker, mission_name, timestamp=None):

    if timestamp is not None:
        current_speaker = speaker.current_shift(timestamp)
    else:
        current_speaker = speaker

    short_name_lang = ''
    if current_speaker.short_name_lang:
        short_name_lang = " lang='%s'"  % current_speaker.short_name_lang 
    detail = """
      <img src='%(MISSIONS_STATIC_URL)s%(mission_name)s/images/avatars/%(avatar)s' alt='' width='48' height='48' %(short_name_lang)salt='%(short_name)s'>
    """ % {
        "avatar": current_speaker.avatar,
        "short_name": current_speaker.short_name,
        "short_name_lang": short_name_lang,
        "mission_name": mission_name,
        "MISSIONS_STATIC_URL": settings.MISSIONS_STATIC_URL,
    }

    url = None
    if current_speaker.role == 'mission-ops':
        url = '%s#%s' % (reverse("people", kwargs={"role": current_speaker.role}), current_speaker.slug)
    elif current_speaker.role == 'astronaut' or current_speaker.role == 'mission-ops-title':
        url = '%s#%s' % (reverse("people"), current_speaker.slug)

    if url:
        return "<a href='%s'>%s</a>" % (url, detail)
    else:
        return detail

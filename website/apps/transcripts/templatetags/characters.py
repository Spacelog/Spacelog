from django.template import Library
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.html import format_html
from .missionstatic import mission_static

register = Library()


def avatar_url(speaker, mission_name):
    return mission_static(mission_name, "images/avatars", speaker.avatar)


@register.simple_tag
def avatar_and_name(speaker, mission_name, timestamp=None):

    if timestamp is not None:
        current_speaker = speaker.current_shift(timestamp)
    else:
        current_speaker = speaker

    short_name_lang = ''
    if current_speaker.short_name_lang:
        short_name_lang = format_html(" lang='{}'", current_speaker.short_name_lang)

    detail = format_html("""
          <img src='{avatar}' alt='' width='48' height='48'>
          <span{short_name_lang}>{short_name}</span>
        """,
        avatar=avatar_url(current_speaker, mission_name),
        short_name=current_speaker.short_name,
        short_name_lang=short_name_lang,
    )

    url = None
    role = current_speaker.role
    if role.endswith('-alias'):
        role = role[:-6]
    if role == 'mission-ops':
        url = '%s#%s' % (reverse("people", kwargs={"role": role}), current_speaker.slug)
    elif role in ('astronaut', 'mission-ops-title'):
        url = '%s#%s' % (reverse("people"), current_speaker.slug)

    if url:
        return format_html("<a href='{}'>{}</a>", url, detail)
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
        short_name_lang = format_html(" lang='{}'", current_speaker.short_name_lang)
    detail = format_html(
        "<img{short_name_lang} src='{avatar}' alt='' width='48' height='48' alt='{short_name}'>",
        avatar=avatar_url(current_speaker, mission_name),
        short_name=current_speaker.short_name,
        short_name_lang=short_name_lang,
    )

    url = None
    role = current_speaker.role
    if role.endswith('-alias'):
        role = role[:-6]
    if role == 'mission-ops':
        url = '%s#%s' % (reverse("people", kwargs={"role": role}), current_speaker.slug)
    elif role in ('astronaut', 'mission-ops-title'):
        url = '%s#%s' % (reverse("people"), current_speaker.slug)

    if url:
        return format_html("<a href='{}'>{}</a>", url, detail)
    else:
        return detail

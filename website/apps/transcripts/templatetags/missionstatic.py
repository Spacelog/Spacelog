import os
from django import template
from django.contrib.staticfiles.storage import staticfiles_storage


def mission_static(mission, *path):
    full_path = os.path.join('missions', mission, *path)
    return staticfiles_storage.url(full_path)


register = template.Library()
register.simple_tag(mission_static)

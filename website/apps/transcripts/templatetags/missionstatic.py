import os
from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import (
    storages, staticfiles_storage,
)


staticfiles_digest_free_storage = storages["digest_free_staticfiles"]

def full_path(mission, *path):
    """
    Builds a full asset path from a mission name, and an arbitrary number of
    path components.
    """

    return os.path.join('missions', mission, *path)


def digest_free_static(path):
    """
    Uses storages["digest_free_staticfiles"] instead of storages["staticfiles"]
    to produce a URL that doesn't include the digest of the file's current
    contents.

    This is useful for passing URLs to the Open Graph, which will continue to
    use the same URL more-or-less forever. If we gave it a digested URL, we
    wouldn't be able to update the file.
    """

    return staticfiles_digest_free_storage.url(path)


def mission_static(mission, *path):
    """
    Returns the URL of a mission static asset.
    """

    return staticfiles_storage.url(full_path(mission, *path))


def digest_free_mission_static(mission, *path):
    """
    Returns the URL of a mission static asset, without the digest of the
    file contents in the URL.

    See digest_free_static for all the gory details.
    """

    return staticfiles_digest_free_storage.url(full_path(mission, *path))


register = template.Library()
register.simple_tag(digest_free_static)
register.simple_tag(mission_static)
register.simple_tag(digest_free_mission_static)

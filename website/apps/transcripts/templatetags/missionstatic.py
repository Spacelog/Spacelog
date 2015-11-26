import os
from django import template
from django.contrib.staticfiles.storage import (
    StaticFilesStorage, staticfiles_storage,
)


def full_path(mission, *path):
    """
    Builds a full asset path from a mission name, and an arbitrary number of
    path components.
    """

    return os.path.join('missions', mission, *path)


def digest_free_static(path):
    """
    Bypasses the configured static files storage and uses the default
    StaticFilesStorage class instead, to produce a URL that doesn't include
    the digest of the file's current contents.

    This is useful for passing URLs to the Open Graph, which will continue to
    use the same URL more-or-less forever. If we gave it a digested URL, we
    wouldn't be able to update the file.

    As long as the configured static files storage is one of the standard
    subclasss of StaticFilesStorage--like ManifestStaticFilesStorage--this
    should all be fine.
    """

    digest_free_storage = StaticFilesStorage()
    return digest_free_storage.url(path)


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

    return digest_free_static(full_path(mission, *path))


register = template.Library()
register.simple_tag(digest_free_static)
register.simple_tag(mission_static)
register.simple_tag(digest_free_mission_static)

"""
Various utility functions which we don't want to expose as first-class fabric commands,
but which are very helpful in building up commands.
"""


from fabric.api import *
from fabric.contrib.files import exists
import os
import os.path
import socket
import tempfile

### SOURCE CONTROL EXPORT & UPLOAD

def export_and_upload_tar_from_git():
    """Create an archive from the git remote."""

    require('release')

    export_tar_from_git()
    upload_tar()


def export_and_upload_tar_from_git_local():
    """Create an archive from the local repo."""

    require('release')

    export_tar_from_git_local()
    upload_tar()


def export_tar_from_git():
    """Create an archive from the git remote."""

    require('release', 'remote', 'branch')

    local("git archive --format=tar --prefix=%(release)s/ --remote='%(remote)s' %(branch)s | gzip -c > %(release)s.tar.gz" % {
        'release': env.release,
        'remote': env.remote,
        'branch': env.branch,
        }
    )


def export_tar_from_git_local():
    """Create an archive from the git local."""

    require('release', 'branch')

    local("git archive --format=tar --prefix=%(release)s/ %(branch)s | gzip -c > %(release)s.tar.gz" % {
        'release': env.release,
        'branch': env.branch,
        }
    )


def upload_tar():
    """Upload a release tar and unpack it."""

    require('hosts', 'release')

    put('%s.tar.gz' % env.release, '%s/archives/' % env.path)
    run(
        "cd %(path)s/releases && "
        "gzip -dc %(path)s/archives/%(release)s.tar.gz | tar xf -" % {
            'path': env.path,
            'release': env.release,
        },
    )
    local('rm %s.tar.gz' % env.release)

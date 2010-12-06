"""
Remote server layout:

PATH/releases -- unpacked versions (versioned by datetime of fabric invocation)
  also current & previous doing the obvious thing (as symlinks)
  within each, ENV a virtualenv just for that version
PATH/archives -- tgz archives of versions

Use the setup action to build the bits you need.
"""

from fabric.api import *
from fabric.contrib.files import exists
import tempfile
import os

env.branch = "master"

# App choices

def artemis():
    env.django_project_name = 'artemis'
    env.staging_hosts = ['core.fort'] # old, aww
    env.live_hosts = ['spacelog.org']
    env.user = 'spacelog'
    env.path = '/home/spacelog'

# only one app
artemis()

# Environment choices

def staging():
    env.hosts = env.staging_hosts
    env.environment = 'staging'

def live():
    env.hosts = env.live_hosts
    env.environment = 'live'

# tasks

def dirty_deploy():
    """
    Do a dirty deploy. For some reason, fab doesn't want to let me pass True through
    to the dirty parameter of deploy().
    """
    deploy(True)

def deploy(dirty=False):
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules and then restart the webserver
    """
    require('hosts')
    require('path')

    ponder_release()

    export_and_upload_tar_from_git()
    if dirty:
        copy_previous_virtualenv()
    else:
        make_release_virtualenv()
    prepare_release(dirty)
    switch_to(env.release)
    restart_webserver()

def setup():
    """
    Set up the initial structure for the given user.
    """
    require('hosts')
    require('path')
    
    run("mkdir releases")
    run("mkdir archives")

def switch_to(version):
    """Switch the current (ie live) version"""
    require('hosts')
    require('path')
    
    if exists('%s/releases/previous' % env.path):
        run('rm %s/releases/previous' % env.path)
    if exists('%s/releases/current' % env.path):
        run('mv %s/releases/current %s/releases/previous' % (env.path, env.path))
    run('cd %s; ln -s %s releases/current' % (env.path, version))
    
    env.release = version # in case anything else wants to use it after us

def switch_to_version(version):
    "Specify a specific version to be made live"
    switch_to(version)
    restart_webserver()
    
# Helpers. These are called by other functions rather than directly

def ponder_release():
    import time
    env.release = time.strftime('%Y-%m-%dT%H.%M.%S')

def export_and_upload_tar_from_git():
    "Create an archive from the git local repo."
    require('release', provided_by=[deploy])
    export_tgz_from_git()
    upload_tar()

def export_tgz_from_git():
    "Create an archive from the git local repo."
    local("git archive --format=tar --prefix=%(release)s/ %(branch)s | gzip -c > %(release)s.tar.gz" % {
        'release': env.release,
        'branch': env.branch,
        }
    )

def upload_tar():
    require('release', provided_by=[deploy])
    require('path', provided_by=[deploy])

    put('%s.tar.gz' % env.release, '%s/archives/' % env.path)
    run('cd %s/releases && gzip -dc ../archives/%s.tar.gz | tar xf -' % (env.path, env.release))
    local('rm %s.tar.gz' % env.release)

def copy_previous_virtualenv():
    "Copy a previous virtualenv, for when making a new one is too much of a PITA"
    require('release', provided_by=[deploy])
    run(
        "cp -a %(path)s/releases/current/ENV %(path)s/releases/%(release)s/ENV" % {
            'path': env.path,
            'release': env.release,
        }
    )

def make_release_virtualenv():
    "Make a virtualenv and install the required packages into it"
    require('release', provided_by=[deploy])
    new_release_virtualenv()
    update_release_virtualenv()
    
def new_release_virtualenv():
    "Create a new virtualenv, install pip, and upgrade setuptools"
    require('release', provided_by=[deploy])
    run(
        "cd %(path)s/releases/%(release)s; "
        "virtualenv ENV; "
        "ENV/bin/easy_install pip; "
        "ENV/bin/easy_install -U setuptools" % {
            'path': env.path,
            'release': env.release
        }
    )
    
def update_release_virtualenv():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy])
    run(
        "cd %(path)s/releases/%(release)s; "
        "ENV/bin/pip --default-timeout=600 install -r requirements.txt" % {
            'path': env.path,
            'release': env.release
        }
    )

def prepare_release(dirty=False):
    "Do any release-local build actions."
    require('release', provided_by=[deploy])
    if dirty:
        # basically, don't reindex, but copy the xappydb from the
        # currently-running deploy (in ../current)
        run(
            "make -C %(path)s/releases/%(release)s/ dirty" % {
                'environment': env.environment,
                'path': env.path,
                'project': env.django_project_name,
                'release': env.release
            }
        )
    else:
        run(
            "make -C %(path)s/releases/%(release)s/" % {
                'environment': env.environment,
                'path': env.path,
                'project': env.django_project_name,
                'release': env.release
            }
        )
    make_local_settings()

def make_local_settings():
    """
    make local_settings.py for both global & website that change
    the deployed URLs for static files (both global and mission-specific)
    to use env.release in their paths.
    
    then put it up to the release on live
    """
    require('release', provided_by=[deploy])

    (fd, fname) = tempfile.mkstemp()
    os.write(fd, """
# Override the default CDN URLs to use this release's timestamp
# (website)
STATIC_URL = 'http://cdn.spacelog.org/%(release)s/assets/website/'
MISSIONS_STATIC_URL = 'http://cdn.spacelog.org/%(release)s/assets/website/missions/'
""" % {
        'release': env.release,
    }
    )
    os.close(fd)
    put(
        fname,
        '%(path)s/releases/%(release)s/website/local_settings.py' % {
            'path': env.path,
            'release': env.release,
        }
    )
    os.unlink(fname)

    (fd, fname) = tempfile.mkstemp()
    os.write(fd, """
# Override the default CDN URLs to use this release's timestamp
# (global)
STATIC_URL = 'http://cdn.spacelog.org/%(release)s/assets/global/'
MISSIONS_STATIC_URL = 'http://cdn.spacelog.org/%(release)s/assets/website/missions/'
""" % {
        'release': env.release,
    }
    )
    os.close(fd)
    put(
        fname,
        '%(path)s/releases/%(release)s/global/local_settings.py' % {
            'path': env.path,
            'release': env.release,
        }
    )
    os.unlink(fname)

def restart_webserver():
    "Restart the web server"
    run("userv root apache2-reload")

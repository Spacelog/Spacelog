"""Basic fabfile for Spacelog. See DEPLOY.md to get started.

Generally:

$ fab -H host deploy

If the missions need re-indexing:

$ fab -H host deploy:bootstrap=true

Remote server layout:

archives            tgz archives of code versions
releases            unpacked, versioned by datetime of fabric invocation
releases/current    symlink to current version
releases/previous   symlink to previous version
releases/next       symlink to version being upgraded to
releases/<>/ENV     virtualenv per release
"""

from fabric.api import *
from fabric.contrib.files import exists
import os
import time

import fabhelpers


env.remote = 'git@github.com:Spacelog/Spacelog.git'
env.branch = 'HEAD'
env.project = 'spacelog'

env.user = 'spacelog'
env.path = '/home/%s' % env.user


def deploy(restart='true', bootstrap='false'):
    """
    Deploy the latest version of the site to the servers.

    restart => restart app servers, otherwise just start
    bootstrap => build database &c, otherwise just make new release workable

    Basically, if anything other than code and templates has changed, you
    need to bootstrap. (This isn't precisely true, but it's simpler to
    think this way because the most common changes are for new missions
    or changes to missions, which requires a reindex.)
    """

    _bootstrap = (bootstrap in ('true', 'True'))
    if _bootstrap:
        restart = False
    else:
        restart = (restart in ('true', 'True'))

    # installs any required third party modules, compiles static files
    # and messages, migrates the database and then restarts the
    # appserver

    env.release = time.strftime('%Y-%m-%dT%H.%M.%S')

    # github doesn't support upload-archive, so work from local repo
    fabhelpers.export_and_upload_tar_from_git_local()
    prep_release(env.release, bootstrap)
    switch_to(env.release)
    if restart:
        restart_appserver()
    else:
        start_appserver()


def switch_to(version):
    """Switch the current (ie live) version."""

    require('hosts')

    previous_path = os.path.join(env.path, 'releases', 'previous')
    current_path = os.path.join(env.path, 'releases', 'current')
    if exists(previous_path):
        run('rm %s' % previous_path)
    if exists(current_path):
        run('mv %s %s' % (current_path, previous_path))
    # ln -s doesn't actually take a path relative to cwd as its first
    # argument; it's actually relative to its second argument
    run('ln -s %s %s' % (version, current_path))
    # tidy up the next marker if there was one
    run('rm -f %s' % os.path.join(env.path, 'releases', 'next'))

    env.release = version # in case anything else wants to use it after us


def prep_release(version, bootstrap='false'):
    """Update virtualenv and make release workable."""

    require('hosts')
    bootstrap = (bootstrap in ('true', 'True'))

    current_path = os.path.join(env.path, 'releases', 'current')
    next_path = os.path.join(env.path, 'releases', 'next')
    if exists(next_path):
        run('rm %s' % next_path)
    run('ln -s %s %s' % (version, next_path))

    run(
        "cd %(next_path)s; "
        "if [ -d %(current_path)s/ENV ]; then "
        "    cp -a %(current_path)s/ENV %(next_path)s/ENV; "
        "else "
        "    virtualenv --system-site-packages ENV; "
        "fi; "
        "ENV/bin/pip install -r requirements.txt" % {
            'path': env.path,
            'next_path': next_path,
            'current_path': current_path,
            'release': env.release
        }
    )

    if bootstrap:
        # Almost identical to reindex(), but works before
        # we've switched.
        run(
            'make -C %(next_path)s all' % {
                'next_path': next_path,
            }
        )
    else:
        run(
            'make -C %(next_path)s dirty' % {
                'next_path': next_path,
            }
        )

    # leave the next marker (symlink) in place in case something
    # goes wrong before the end of switch_to, since it will provide
    # useful state on the remote machine


def reindex():
    """
    Rebuild the missions database (plus stats graphs).
    """
    require('hosts')
    current_path = os.path.join(env.path, 'releases', 'current')
    run(
        'make -C %(path)s reindex statsporn' % {
            'path': current_path,
        }
    )


def restart_appserver():
    """Restart the (gunicorn) app server."""

    require('hosts')
    current_path = os.path.join(env.path, 'releases', 'current')
    run(
        'make -C %(path)s gunicornicide gunicornucopia' % {
            'path': current_path,
        }
    )


def start_appserver():
    """Start the (gunicorn) app server."""

    require('hosts')
    current_path = os.path.join(env.path, 'releases', 'current')
    run(
        'cd %(path)s; make gunicornucopia' % {
            'path': current_path,
        }
    )


def update_vhosts():
    """Copy VHOSTS into place. Run after deploy."""

    sudo(
        'cp /home/spacelog/releases/current/website/configs/live/website.vhost /etc/apache2/sites-available/000-website.conf && '
        'cp /home/spacelog/releases/current/global/configs/live/global.vhost /etc/apache2/sites-available/global.conf && '
        'a2ensite 000-website global && '
        'service apache2 reload'
    )

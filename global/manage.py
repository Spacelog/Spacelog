#!/usr/bin/env python

import os
import sys

# where are we? eh?
project_path = os.path.realpath(os.path.dirname(__file__))

# we add them first in case we want to override anything already on the system
sys.path.insert(0, project_path)
sys.path.insert(0, os.path.join(project_path, '../'))

import ext

from django.core.management import execute_manager
args = sys.argv
# Let's figure out our environment
if os.environ.has_key('DJANGOENV'):
    environment = os.environ['DJANGOENV']
elif len(sys.argv) > 1:
    # this doesn't currently work
    environment = sys.argv[1]
    if os.path.isdir(os.path.join(project_path, 'configs', environment)):
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    else:
        environment = None
else:
    environment = None
try:
    module = "configs.%s.settings" % environment
    __import__(module)
    settings = sys.modules[module]
    # worked, so add it into the path so we can import other things out of it
    sys.path.insert(0, os.path.join(project_path, 'configs', environment))
except ImportError:
    environment = None

# We haven't found anything helpful yet, so use development.
if environment == None:
    try:
        import configs.development.settings
        settings = configs.development.settings
        environment = 'development'
        sys.path.insert(0, os.path.join(project_path, 'configs', environment))
    except ImportError:
        sys.stderr.write("Error: Can't find the file 'settings.py'; looked in %s and development.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % (environment,))
        sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)

from configs.settings import *
# The following MUST be an absolute URL in live deploys (it's given out
# to other systems). Also, it doesn't get overridden in local_settings.py
# unlike the others.
FIXED_MISSIONS_STATIC_URL = 'http://cdn.spacelog.org/assets/website/missions/'

STATIC_URL = 'http://cdn.spacelog.org/assets/website/'
MISSIONS_STATIC_URL = 'http://cdn.spacelog.org/assets/website/missions/'
MISSIONS_PNG_URL = 'http://cdn.spacelog.org/assets/website/missions/'

# allow local overrides, probably built during deploy
try:
    from local_settings import *
except ImportError:
    pass

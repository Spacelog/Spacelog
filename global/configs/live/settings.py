from configs.settings import *

ALLOWED_HOSTS = [
    '.spacelog.org',
]

# The following MUST be an absolute URL in live deploys (it's given out
# to other systems).
STATIC_URL = 'http://cdn.spacelog.org/assets/global/'

# I believe the next line to be true, although /assets/global/missions/ works too;
# this feels more correct.
MISSIONS_STATIC_URL = 'http://cdn.spacelog.org/assets/website/missions/'

# allow local overrides, probably built during deploy
try:
    from local_settings import *
except ImportError:
    pass

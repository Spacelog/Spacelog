from configs.settings import *
STATIC_URL = 'http://cdn.spacelog.org/assets/website/'
MISSIONS_STATIC_URL = 'http://cdn.spacelog.org/assets/website/missions/'
MISSIONS_PNG_URL = 'http://cdn.spacelog.org/assets/website/missions/'

# allow local overrides, probably built during deploy
try:
    from local_settings import *
except ImportError:
    pass

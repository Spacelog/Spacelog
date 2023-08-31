from configs.settings import *

ALLOWED_HOSTS = [
    '.' + os.getenv('PROJECT_DOMAIN', 'spacelog.org'),
    'localhost',
    '.spacelog.org',
]

# This should be shared between all releases, so that the previous
# release's assets are still available (particularly important with
# upstream caching that may take a while to roll over).
STATIC_ROOT = '/home/spacelog/assets/global'

# allow local overrides, probably built during deploy
try:
    from local_settings import *
except ImportError:
    pass

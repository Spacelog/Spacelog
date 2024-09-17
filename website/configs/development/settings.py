from configs.settings import *

DEBUG = True
ALLOWED_HOSTS = [
    '.dev.spacelog.org',
    '.localhost',
]

try:
    from local_settings import *
except ImportError:
    pass

STATICFILES_DIRS += [
    "/home/spacelog/assets/website"
]

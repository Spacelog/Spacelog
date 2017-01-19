from configs.settings import *

DEBUG = True
PROJECT_HOME = "http://dev.spacelog.org:8001/"
ALLOWED_HOSTS = [
    '.dev.spacelog.org',
]

try:
    from local_settings import *
except ImportError:
    pass

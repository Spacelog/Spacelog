from configs.settings import *

DEBUG = True
PROJECT_DOMAIN = "dev.spacelog.org:8000"

try:
    from local_settings import *
except ImportError:
    pass

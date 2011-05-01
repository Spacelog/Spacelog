from configs.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PROJECT_HOME = "http://dev.spacelog.org:8001/"

try:
    from local_settings import *
except ImportError:
    pass

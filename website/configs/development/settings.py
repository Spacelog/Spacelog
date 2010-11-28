from configs.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PROJECT_HOME = "http://artemis:3000/"

try:
    from local_settings import *
except ImportError:
    pass

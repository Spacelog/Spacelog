from configs.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

try:
    from local_settings import *
except ImportError:
    pass

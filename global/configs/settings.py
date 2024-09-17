# Django settings for website project.

import os
import django
import sys

# calculated paths for django and the site
# used as starting points for various other paths
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(os.path.join(SITE_ROOT, 'apps'))

DEBUG = False

LOGLEVEL = os.getenv('DJANGO_LOGLEVEL', 'info').upper()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'level': LOGLEVEL,
            'handlers': ['console',],
        },
    },
}

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
    "digest_free_staticfiles": {
        "BACKEND": 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}
STATICFILES_DIRS = [
    os.path.join(SITE_ROOT, 'static'),
]

MISSIONS_ROOT = os.path.join(SITE_ROOT, '..', 'missions')
for mission_name in os.listdir(MISSIONS_ROOT):
    mission_image_path = os.path.join(MISSIONS_ROOT, mission_name, 'images')
    if os.path.isdir(mission_image_path):
        STATICFILES_DIRS += [
            ("missions/%s/images" % mission_name, mission_image_path),
        ]

STATIC_ROOT = os.path.join(SITE_ROOT, 'collected')
STATIC_URL = '/assets/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'hqp*)4r*a99h4@=7@5bpdn+ik8+x9c&=zk4o-=w1ap6n!9_@z1'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(SITE_ROOT, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
            ],
        },
    },
]

MIDDLEWARE = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'homepage.middleware.RedisMiddleware',
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'homepage',
    'search',
    'website.apps.transcripts',
    'website.apps.common',
)

WEBSITE_LINK_PORT = os.getenv('WEBSITE_LINK_PORT', '80')
PROJECT_DOMAIN = os.getenv('PROJECT_DOMAIN', 'spacelog.org')
if WEBSITE_LINK_PORT.strip() and WEBSITE_LINK_PORT != '80':
    PROJECT_DOMAIN = '%s:%s' % (PROJECT_DOMAIN, WEBSITE_LINK_PORT)

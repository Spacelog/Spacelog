from configs.settings import *

ALLOWED_HOSTS = [
    '.spacelog.org',
]

# Transcript media (such as inline images), and original transcript
# page images, are stored separately to the repo, and hence managed
# (on S3) distinctly from the codebase. This does mean that launching
# a new mission *REQUIRES* uploading something (typically the
# transcript cover) to {{ mission }}/images/original/TEC/about.png to
# avoid breaking the mission 'about' page fairly obviously. But we
# really need everything up there, assuming page numbers are defined
# in the transcript.
MISSIONS_IMAGE_URL = 'http://media.spacelog.org/'

# This should be shared between all releases, so that the previous
# release's assets are still available (particularly important with
# upstream caching that may take a while to roll over).
STATIC_ROOT = '/home/spacelog/assets/website'

# allow local overrides, probably built during deploy
try:
    from local_settings import *
except ImportError:
    pass

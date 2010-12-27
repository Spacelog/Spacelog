import boto
from boto.s3.key import Key
import os
import sys

BUCKET = 'spacelog'
TTL = 86400*7

if len(sys.argv) != 3:
    print "Usage s3-upload.py <directory> <upload path>"
    sys.exit(1)

conn = boto.connect_s3()
bucket = conn.get_bucket(BUCKET)
files = os.listdir(sys.argv[1])

for file in files:
    print "Uploading", file
    k = Key(bucket, '%s/%s' % (sys.argv[2], file))
    k.set_contents_from_filename("%s/%s" % (sys.argv[1], file),
                headers={'Cache-Control': 'max-age=%s' % TTL})
    k.set_acl('public-read')

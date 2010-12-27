#!/usr/bin/env python
# You'll need to set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# environment variables to make this work.
# (or ask Russ)

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

remote_files = set([key.name.split('/')[-1] for key in bucket.list(sys.argv[2])])

files = os.listdir(sys.argv[1])

for file in files:
    if file not in remote_files:
        print "Uploading", file
        k = Key(bucket, '%s/%s' % (sys.argv[2], file))
        k.set_contents_from_filename("%s/%s" % (sys.argv[1], file),
                headers={'Cache-Control': 'max-age=%s' % TTL})
        k.set_acl('public-read')

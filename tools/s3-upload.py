#!/usr/bin/env python
# You'll need to set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# environment variables to make this work.
# (or ask Russ)

import boto
from boto.s3.key import Key
import os
from os import path
import sys

BUCKET = 'spacelog'
TTL = 86400 * 7

if len(sys.argv) != 3:
    print("Usage s3-upload.py <directory> <upload path>")
    sys.exit(1)

conn = boto.connect_s3()
bucket = conn.get_bucket(BUCKET)

for root, _, filenames in os.walk(sys.argv[1]):
    for filename in filenames:
        local_path = path.join(path.abspath(root), filename)
        remote_path = path.abspath(path.join(sys.argv[2], root, filename))
        k = Key(bucket, remote_path)
        if not k.exists():
            print("Uploading %s" % remote_path)
            k.set_contents_from_filename(local_path,
                                         headers={'Cache-Control': 'max-age=%s' % TTL})
            k.set_acl('public-read')

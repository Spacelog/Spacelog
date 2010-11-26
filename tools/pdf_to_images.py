#!/usr/bin/env python
import os
import subprocess
import sys

if len(sys.argv) < 2:
    print >>sys.stderr, "Usage: python pdf_to_images.py [pdf file]"
    print >>sys.stderr
    print >>sys.stderr, "Converts a PDF into a directory full of PNGs. Requires ImageMagick."
    sys.exit(1)

pdf_file = sys.argv[1]
output_dir = '%s_images' % pdf_file
os.mkdir(output_dir)

page = 1

while True:
    print "Converting page %s..." % page
    exit_code = subprocess.call([
        'convert', 
        '-density', '300', 
        u'%s[%s]' % (pdf_file, page-1), # zero indexed pages
        os.path.join(output_dir, '%s.png' % page),
    ])
    if exit_code != 0:
        break
    page += 1



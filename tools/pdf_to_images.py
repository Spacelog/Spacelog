#!/usr/bin/env python
import os
import subprocess
import sys

OPTIMISE_IMAGES = False

if len(sys.argv) < 2:
    print >>sys.stderr, "Usage: python pdf_to_images.py [pdf file]"
    print >>sys.stderr
    print >>sys.stderr, "Converts a PDF into a directory full of PNGs. Requires ImageMagick and optipng."
    sys.exit(1)

pdf_file = sys.argv[1]
output_dir = '%s_images' % pdf_file
os.mkdir(output_dir)

page = 1

while True:
    print "Converting page %s..." % page
    png_file = os.path.join(output_dir, '%s.png' % page)

    exit_code = subprocess.call([
        'convert', 
        '-density', '300', 
        u'%s[%s]' % (pdf_file, page-1), # zero indexed pages
	png_file,
    ])
    if exit_code != 0:
        break
    
    if OPTIMISE_IMAGES:
        # This usually takes many times longer than the extract
        print "Optimising %s..." % png_file
        subprocess.call([
            'optipng',
            '-q',
            '-o7',
            png_file,
        ])
        if exit_code != 0:
            print >>sys.stderr, "optipng failed"
            sys.exit(1)

    page += 1



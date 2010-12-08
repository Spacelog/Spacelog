#!/usr/bin/env python
import os
import subprocess
import sys

OPTIMISE_IMAGES = True
ORIGINALS_WIDTH = 770
ABOUT_PAGE      = 1
ABOUT_WIDTH     = 270


if len(sys.argv) < 2:
    print >>sys.stderr, "Usage: python pdf_to_images.py [pdf file]"
    print >>sys.stderr
    print >>sys.stderr, "Converts a PDF into a directory full of PNGs. Requires ImageMagick and optipng."
    sys.exit(1)

pdf_file = sys.argv[1]
output_dir = '%s_images' % pdf_file
os.mkdir(output_dir)

page = 1

def generate_image( image_name, page, resize_dimensions=None ):
    png_file = os.path.join(output_dir, '%s.png' % image_name)

    print "Converting page %s to %s..." % ( page, png_file )
    exit_code = subprocess.call([
        'convert', 
        '-density', '300', 
        '-resize', resize_dimensions,
        u'%s[%s]' % (pdf_file, page-1), # zero indexed pages
        png_file,
    ])
    
    if OPTIMISE_IMAGES:
        # This usually takes many times longer than the extract
        print "Optimising %s..." % png_file
        optimise_exit_code = subprocess.call([
            'optipng',
            '-q',
            '-o7',
            png_file,
        ])
        if optimise_exit_code != 0:
            print >>sys.stderr, "optipng failed"
            sys.exit(1)
    
    return exit_code


while True:
    if page == ABOUT_PAGE:
        exit_code = generate_image( 'about', page, '%i' % ABOUT_WIDTH )
        if exit_code != 0:
            break
    
    exit_code = generate_image( '%i' % page, page, '%i' % ORIGINALS_WIDTH )
    if exit_code != 0:
        break
    
    page += 1



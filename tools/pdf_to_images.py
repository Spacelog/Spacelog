#!/usr/bin/env python
import os
import subprocess
import sys
import tempfile

ORIGINALS_WIDTH = 770
ABOUT_PAGE      = 1
ABOUT_WIDTH     = 270

requires = {
    'ImageMagick': 'convert',
    'OptiPNG'    : 'optipng',
}

unmet_requirements = []
for name, command in requires.items():
    tf = tempfile.TemporaryFile()
    try:
        subprocess.call( command, stdin=None, stdout=tf, stderr=tf )
    except OSError:
        unmet_requirements += [ '%s (%s)' % ( name, command ) ]

if unmet_requirements:
    print('Unmet requirements: %s' % ', '.join( unmet_requirements ), file=sys.stderr)
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python pdf_to_images.py [pdf file]", file=sys.stderr)
    print(file=sys.stderr)
    print("Converts a PDF into a directory full of PNGs. Requires ImageMagick and optipng.", file=sys.stderr)
    sys.exit(1)

pdf_file = sys.argv[1]
output_dir = '%s_images' % pdf_file
os.mkdir(output_dir)

page = 1

def generate_image( image_name, page, resize_dimensions=None ):
    png_file = os.path.join(output_dir, '%s.png' % image_name)
    
    # Convert and resize in two passes to get the smallest filesize
    print("Converting page %s to %s..." % ( page, png_file ))
    exit_code = subprocess.call([
        'convert', 
        '-density', '300', 
        '%s[%s]' % (pdf_file, page-1), # zero indexed pages
        png_file,
    ])
    
    if not exit_code:
        print("Resizing %s..." % png_file)
        # HACK: Assumes that the input image is black and white,
        #       and 16 colors will suffice for antialiasing
        exit_code = subprocess.call([
            'convert', 
            '-colorspace', 'Gray',
            '-resize', resize_dimensions,
            '-colors', '16',
            png_file,
            png_file,
        ])
        
    if not exit_code:
        # This usually takes many times longer than the extract
        print("Optimising %s..." % png_file)
        optimise_exit_code = subprocess.call([
            'optipng',
            '-q',
            '-o7',
            png_file,
        ])
        if optimise_exit_code != 0:
            print("optipng failed", file=sys.stderr)
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



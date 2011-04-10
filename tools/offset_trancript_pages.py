#!/usr/bin/env python

import os, sys

if len(sys.argv) < 3:
    print >>sys.stderr, "Usage: python offset_transcript_pages.py [transcript file] [offset]"
    print >>sys.stderr
    print >>sys.stderr, "Mass-modifies transcript page numbers by a specified offset."
    sys.exit(1)

transcript_file = sys.argv[1]
offset          = int( sys.argv[2] )

os.rename( transcript_file, transcript_file+"~" )
source      = open( transcript_file+"~", "r" )
destination = open( transcript_file, "w" )

for line in source:
    fixed_line = line
    if line.startswith( '_page' ):
        page = int( line.strip( '_page: ' ) )
        page += offset
        fixed_line = "_page : %d\n" % page
    
    destination.write( fixed_line )

source.close()
destination.close()
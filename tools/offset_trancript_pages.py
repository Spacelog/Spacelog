#!/usr/bin/env python

import os, sys

if len(sys.argv) < 3:
    print("Usage: python offset_transcript_pages.py [transcript file] [offset]", file=sys.stderr)
    print(file=sys.stderr)
    print("Mass-modifies transcript page numbers by a specified offset.", file=sys.stderr)
    sys.exit(1)

transcript_file = sys.argv[1]
offset          = int( sys.argv[2] )

os.rename( transcript_file, transcript_file+"~" )
source      = open( transcript_file+"~", encoding="utf-8" )
destination = open( transcript_file, "w", encoding="utf-8" )

for line in source:
    fixed_line = line
    if line.startswith( '_page' ):
        page = int( line.strip( '_page: ' ) )
        page += offset
        fixed_line = "_page : %d\n" % page
    
    destination.write( fixed_line )

source.close()
destination.close()
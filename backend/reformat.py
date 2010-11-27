"""
When run as a module, reads the file provided on the command line
and outputs on stdout a slightly nicer file format.
"""

import sys
from backend.parser import TranscriptParser
from backend.util import seconds_to_timestamp

def reformat(filename):
    parser = TranscriptParser(filename)
    for chunk in parser.get_chunks():
        timestamp = seconds_to_timestamp(chunk['timestamp'])
        for line in chunk['lines']:
            print "%s\t%s:\t %s" % (
                timestamp,
                line['speaker'],
                line['text'],
            )

if __name__ == "__main__":
    try:
        reformat(sys.argv[1])
    except IndexError:
        print "Please pass a file to reformat"


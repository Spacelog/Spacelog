import os
import redis
import pprint

from parser import FileParser

class Indexer(object):
    """
    Parses a file and indexes it.
    """

    def __init__(self, redis_conn, file_parser):
        self.redis_conn = redis_conn
        self.file_parser = file_parser

    def index(self):
        # Delete the old things in the database
        # TODO: More sensible flush/switching behaviour
        self.redis_conn.flushdb()
        for chunk in self.file_parser.get_chunks():
            # First, create a record with the byte offset
            log_line_id = "%s:%i" % (self.file_parser.name, chunk['timestamp'])
            self.redis_conn.set("stream:%s:offset" % log_line_id, chunk['offset'])
            # Add that logline ID for the people involved
            speakers = set([ line['speaker'] for line in chunk['lines'] ])
            for speaker in speakers:
                self.redis_conn.sadd("speaker:%s" % speaker, log_line_id)

if __name__ == "__main__":
    os.environ['TRANSCRIPT_ROOT'] = "../transcript-file-format/"

    redis_conn = redis.Redis()

    fp = FileParser("a13/TEC")
    idx = Indexer(redis_conn, fp)
    idx.index()

    from api import LogLine
    l = LogLine(redis_conn, "a13/TEC", 12)
    print l


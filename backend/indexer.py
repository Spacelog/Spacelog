import os
import redis
import pprint

from parser import FileParser

class Indexer(object):
    """
    Parses a file and indexes it.
    """

    LINES_PER_PAGE = 2

    def __init__(self, redis_conn, file_parser):
        self.redis_conn = redis_conn
        self.file_parser = file_parser

    def index(self):
        # Delete the old things in the database
        # TODO: More sensible flush/switching behaviour
        self.redis_conn.flushdb()
        
        current_labels = {}
        current_transcript_page = None
        current_page = 1
        current_page_lines = 0

        for chunk in self.file_parser.get_chunks():
            log_line_id = "%s:%i" % (self.file_parser.name, chunk['timestamp'])
            # If we've filled up the current page, go to a new one
            if current_page_lines >= self.LINES_PER_PAGE:
                current_page += 1
                current_page_lines = 0
            # See if there's transcript page info, and update it if so
            if chunk['meta'].get('_page', 0):
                current_transcript_page = int(chunk["meta"]['_page'])
            if current_transcript_page:
                self.redis_conn.set("log_line:%s:page" % log_line_id, current_transcript_page)
            # First, create a record with some useful information
            self.redis_conn.hmset(
                    "log_line:%s:info" % log_line_id,
                    {
                        "offset": chunk['offset'],
                        "page": current_page,
                        "transcript_page": current_transcript_page,
                    }
            )
            # Also store the text
            for line in chunk['lines']:
                self.redis_conn.rpush(
                        "log_line:%s:lines" % log_line_id,
                        "%(speaker)s: %(text)s" % line,
                )
            # Add that logline ID for the people involved
            speakers = set([ line['speaker'] for line in chunk['lines'] ])
            for speaker in speakers:
                self.redis_conn.sadd("speaker:%s" % speaker, log_line_id)
            # Add it into the stream and everything sets
            self.redis_conn.sadd("all", log_line_id)
            self.redis_conn.sadd("stream:%s" % self.file_parser.name, log_line_id)
            # Read the new labels into current_labels
            if '_labels' in chunk['meta']:
                for label, endpoint in chunk['meta']['_labels'].items():
                    if endpoint is not None and label not in current_labels:
                        current_labels[label] = endpoint
                    elif label in current_labels:
                        current_labels[label] = max(
                            current_labels[label],
                            endpoint
                        )
                    elif endpoint is None:
                        self.redis_conn.sadd("label:%s" % label, log_line_id)
            # Expire any old labels
            for label, endpoint in current_labels.items():
                # TODO: Decide if we want inclusive or exclusive label endpoints
                if endpoint <= chunk['timestamp']:
                    del current_labels[label]
            # Apply any surviving labels
            for label in current_labels:
                self.redis_conn.sadd("label:%s" % label, log_line_id)
            # Increment the number of log lines we've done
            current_page_lines += len(chunk['lines'])


if __name__ == "__main__":
    os.environ['TRANSCRIPT_ROOT'] = os.path.join( os.path.dirname( __file__ ), '..', "transcript-file-format/" ) 

    redis_conn = redis.Redis()

    fp = FileParser("a13/TEC")
    idx = Indexer(redis_conn, fp)
    idx.index()

    from api import Query
    print list(Query(redis_conn).sort_by_time())


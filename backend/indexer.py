import os
import redis

from parser import TranscriptParser, MetaParser
from api import Act

class TranscriptIndexer(object):
    """
    Parses a file and indexes it.
    """

    LINES_PER_PAGE = 20

    def __init__(self, redis_conn, mission_name, transcript_name, parser):
        self.redis_conn = redis_conn
        self.mission_name = mission_name
        self.transcript_name = transcript_name
        self.parser = parser

    def index(self):
        current_labels = {}
        current_transcript_page = None
        current_page = 1
        current_page_lines = 0
        last_act = None
        previous_log_line_id = None
        launch_time = int(self.redis_conn.get("launch_time:%s" % self.mission_name))
        acts = list(Act.Query(self.redis_conn, self.mission_name))
        for chunk in self.parser.get_chunks():
            timestamp = chunk['timestamp']
            log_line_id = "%s:%i" % (self.transcript_name, timestamp)
            # See if there's transcript page info, and update it if so
            if chunk['meta'].get('_page', 0):
                current_transcript_page = int(chunk["meta"]['_page'])
            if current_transcript_page:
                self.redis_conn.set("log_line:%s:page" % log_line_id, current_transcript_page)
            # Look up the act
            for act in acts:
                if act.includes(timestamp):
                    break
            else:
                raise RuntimeError("No act for timestamp %i" % timestamp)
            # If we've filled up the current page, go to a new one
            if current_page_lines >= self.LINES_PER_PAGE or (last_act is not None and last_act != act):
                current_page += 1
                current_page_lines = 0
            last_act = act
            # First, create a record with some useful information
            self.redis_conn.hmset(
                "log_line:%s:info" % log_line_id,
                {
                    "offset": chunk['offset'],
                    "page": current_page,
                    "transcript_page": current_transcript_page,
                    "act": act.number,
                    "utc_time": launch_time + timestamp,
                }
            )
            # Create the doubly-linked list structure
            if previous_log_line_id:
                self.redis_conn.hset(
                    "log_line:%s:info" % log_line_id,
                    "previous",
                    previous_log_line_id,
                )
                self.redis_conn.hset(
                    "log_line:%s:info" % previous_log_line_id,
                    "next",
                    log_line_id,
                )
            previous_log_line_id = log_line_id
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
            # Add it to the index for this page
            self.redis_conn.rpush("page:%s:%i" % (self.transcript_name, current_page), log_line_id)
            # Add it into the transcript and everything sets
            self.redis_conn.zadd("log_lines:%s" % self.mission_name, log_line_id, chunk['timestamp'])
            self.redis_conn.zadd("transcript:%s" % self.transcript_name, log_line_id, chunk['timestamp'])
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


class MetaIndexer(object):
    """
    Takes a mission folder and reads and indexes its meta information.
    """

    def __init__(self, redis_conn, mission_name, parser):
        self.redis_conn = redis_conn
        self.parser = parser
        self.mission_name = mission_name

    def index(self):
        meta = self.parser.get_meta()

        self.redis_conn.set("launch_time:%s" % self.mission_name, meta['utc_launch_time'])

        for noun in ('act', 'key_scene'):
            for i, data in enumerate(meta.get('%ss' % noun, [])):
                key = "%s:%s:%i" % (noun, self.mission_name, i)
                self.redis_conn.rpush(
                    "%ss:%s" % (noun, self.mission_name),
                    "%s:%i" % (self.mission_name, i),
                )

                data['start'], data['end'] = data['range']
                del data['range']

                self.redis_conn.hmset(key, data)


class MissionIndexer(object):
    """
    Takes a mission folder and indexes everything inside it.
    """

    def __init__(self, redis_conn, folder_path):
        self.redis_conn = redis_conn
        self.folder_path = folder_path
        self.mission_name = folder_path.strip("/").split("/")[-1]

    def index(self):
        # Delete the old things in the database
        # TODO: More sensible flush/switching behaviour
        self.redis_conn.flushdb()
        
        self.index_meta()
        self.index_transcripts()

    def index_transcripts(self):
        for filename in os.listdir(self.folder_path):
            if "." not in filename and filename[0] != "_":
                path = os.path.join(self.folder_path, filename)
                parser = TranscriptParser(path)
                indexer = TranscriptIndexer(self.redis_conn, self.mission_name, "%s/%s" % (self.mission_name, filename), parser)
                indexer.index()

    def index_meta(self):
        path = os.path.join(self.folder_path, "_meta")
        parser = MetaParser(path)
        indexer = MetaIndexer(self.redis_conn, self.mission_name, parser)
        indexer.index()


if __name__ == "__main__":
    print "Indexing..."
    redis_conn = redis.Redis()
    idx = MissionIndexer(redis_conn, os.path.join(os.path.dirname( __file__ ), '..', "transcript-file-format/", "a13")) 
    idx.index()

import os
import redis
import xappy

from backend.parser import TranscriptParser, MetaParser
from backend.api import Act

search_db = xappy.IndexerConnection(
    os.path.join(os.path.dirname(__file__), '..', 'xappydb'),
)

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

        search_db.add_field_action(
            "speaker",
            xappy.FieldActions.STORE_CONTENT,
        )
        search_db.add_field_action(
            "speaker",
            xappy.FieldActions.INDEX_FREETEXT,
            weight=1,
            language='en',
            search_by_default=True,
            allow_field_specific=True,
        )
        search_db.add_field_action(
            "text",
            xappy.FieldActions.STORE_CONTENT,
        )
        search_db.add_field_action(
            "text",
            xappy.FieldActions.INDEX_FREETEXT,
            weight=1,
            language='en',
            search_by_default=True,
            allow_field_specific=False,
            spell=True,
        )
        # FIXME: this should come out of meta
        name_map = {
            'CDR': 'Jim Lovell',
            'CMP': 'Jack Swigert',
            'LMP': 'Fred Haise',
            # not convinced this is suitable for synonyming
            # 'CC': [
            #     'Jack Lousma',
            #     'Vance Brand',
            #     'Joseph Joe Kerwin',
            #     'Ken Mattingly',
            #     'Charlie Charles Duke',
            # ],
        }
        for role, names in name_map.items():
            if type(names) is not list:
                names = list(names)
            for name in names:
                for bit in name.split():
                    search_db.add_synonym(bit, role)
                    search_db.add_synonym(bit, role, field='speaker')

    def add_to_search_index(self, id, text, speakers):
        """
        Take some text and a set of speakers (also text) and add a document
        to the search index, with the id stuffed in the document data.
        """
        doc = xappy.UnprocessedDocument()
        doc.fields.append(xappy.Field("text", text))
        for speaker in speakers:
            doc.fields.append(xappy.Field("speaker", speaker))
        doc.id = id
        try:
            search_db.add(search_db.process(doc))
        except xappy.errors.IndexerError:
            print "umm, error"
            print id, text, speakers
            raise

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
            # Store any images
            for i, image in enumerate(chunk['meta'].get("_images", [])):
                # Make the image id
                image_id = "%s:%s" % (log_line_id, i)
                # Push it onto the images list
                self.redis_conn.rpush(
                    "log_line:%s:images" % log_line_id,
                    image_id,
                )
                # Store the image data
                self.redis_conn.hmset(
                    "image:%s" % image_id,
                    image,
                )
            # Add that logline ID for the people involved
            speakers = set([ line['speaker'] for line in chunk['lines'] ])
            for speaker in speakers:
                self.redis_conn.sadd("speaker:%s" % speaker, log_line_id)
            # And add this logline to search index
            self.add_to_search_index(
                id=log_line_id,
                text=u" ".join(line['text'] for line in chunk['lines']),
                speakers=speakers,
            )
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
                if endpoint < chunk['timestamp']:
                    del current_labels[label]
            # Apply any surviving labels
            for label in current_labels:
                self.redis_conn.sadd("label:%s" % label, log_line_id)
                self.redis_conn.sadd("log_line:%s:labels" % log_line_id, label)
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
        # Index acts and key scenes
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
        # Index glossary information
        for key, data in meta['glossary'].items():
            self.redis_conn.hmset(
                "glossary:%s" % key,
                {
                    "description": data.get('description', ""),
                },
            )


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
                print "Indexing %s..." % filename
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
    redis_conn = redis.Redis()
    idx = MissionIndexer(redis_conn, os.path.join(os.path.dirname( __file__ ), '..', "transcripts/", "a13")) 
    idx.index()
    search_db.flush()

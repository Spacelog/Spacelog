import math
import os
import redis
import xappy

def seconds_to_timestamp(seconds):
    abss = abs(seconds)
    return "%s%02i:%02i:%02i:%02i" % (
        "-" if seconds<0 else "",
        abss // 86400,
        abss % 86400 // 3600,
        abss % 3600 // 60,
        abss % 60,
    )

def floor_and_int(s):
    return int(math.floor(float(s)))

def timestamp_to_seconds(timestamp):
    if timestamp[0]=='-':
        timestamp = timestamp[1:]
        mult = -1
    else:
        mult = 1
    parts = list(map(floor_and_int, timestamp.split(":", 3)))
    return mult * ((parts[0] * 86400) + (parts[1] * 3600) + (parts[2] * 60) + parts[3])

redis_connection = redis.from_url(
    os.environ.get("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

searchdb_location = os.getenv(
    'SEARCHDB_PATH',
    os.path.join(os.path.dirname(__file__), '..', 'xappydb')
)

def get_search_indexer_connection(path=searchdb_location):
    return xappy.IndexerConnection(path)

def get_search_connection(path=searchdb_location):
    return xappy.SearchConnection(path)


class LogLine(object):
    """
    Basic object that represents a log line; pass in the timestamp
    and stream name and it will extract the right bits of data and
    make them accessible via attributes.
    """
    
    def __init__(self, redis_conn, stream_name, timestamp):
        self.redis_conn = redis_conn
        self.stream_name = stream_name
        self.timestamp = timestamp
        self.id = "%s:%i" % (self.stream_name, self.timestamp)
        self._load()

    @classmethod
    def by_log_line_id(cls, redis_conn, log_line_id):
        stream, timestamp = log_line_id.split(":", 1)
        timestamp = int(timestamp)
        return cls(redis_conn, stream, timestamp)

    def _load(self):
        # Find the offset and load just one item from there
        data = self.redis_conn.hgetall("log_line:%s:info" % self.id)
        # Load onto our attributes
        self.page = data['page']
        self.transcript_page = data['transcript_page']
        self.lines = self.redis_conn.lrange("log_line:%s:lines" % self.id, 0, -1)
        self.next_log_line_id = data.get('next', None)
        self.previous_log_line_id = data.get('previous', None)

    def __repr__(self):
        return "<LogLine %s:%i, page %s (%s lines)>" % (self.stream_name, self.timestamp, self.page, len(self.lines))

    def next(self):
        if self.next_log_line_id:
            return LogLine.by_log_line_id(self.redis_conn, self.next_log_line_id)
        else:
            return None

    def previous(self):
        if self.previous_log_line_id:
            return LogLine.by_log_line_id(self.redis_conn, self.previous_log_line_id)
        else:
            return None
    

class Query(object):
    """
    
    """
    def __init__(self, redis_conn, filters=None):
        self.redis_conn = redis_conn
        if filters is None:
            self.filters = {}
        else:
            self.filters = filters

    def _extend_query(self, key, value):
        new_filters = dict(self.filters.items())
        new_filters[key] = value
        return Query(self.redis_conn, new_filters)
    
    def stream(self, stream_name):
        "Returns a new Query filtered by stream"
        return self._extend_query("stream", stream_name)
    
    def range(self, start_time, end_time):
        "Returns a new Query whose results are between two times"
        return self._extend_query("range", (start_time, end_time))
    
    def first_after(self, timestamp):
        "Returns the closest log line after the timestamp."
        if "stream" in self.filters:
            key = "stream:%s" % self.filters['stream']
        else:
            key = "all"
        # Do a search.
        period = 1
        results = []
        while not results:
            results = self.redis_conn.zrangebyscore(key, timestamp, timestamp+period)
            period *= 2
            # This test is here to ensure they don't happen on every single request.
            if period == 8:
                # Use zrange to get the highest scoring element and take its score
                top_score = self.redis_conn.zrange(key, -1, -1, withscores=True)[0][1]
                if timestamp > top_score:
                    raise ValueError("No matching LogLines after timestamp %s." % timestamp)
        # Return the first result
        return self._key_to_instance(results[0])

    def first_before(self, timestamp):
        if "stream" in self.filters:
            key = "stream:%s" % self.filters['stream']
        else:
            key = "all"
        # Do a search.
        period = 1
        results = []
        while not results:
            results = self.redis_conn.zrangebyscore(key, timestamp-period, timestamp)
            period *= 2
            # This test is here to ensure they don't happen on every single request.
            if period == 8:
                # Use zrange to get the highest scoring element and take its score
                bottom_score = self.redis_conn.zrange(key, 0, 0, withscores=True)[0][1]
                if timestamp < bottom_score:
                    raise ValueError("No matching LogLines before timestamp %s." % timestamp)
        # Return the first result
        return self._key_to_instance(results[-1])
    
    def speakers(self, speakers):
        "Returns a new Query whose results are any of the specified speakers"
        return self._extend_query("speakers", speakers)
    
    def labels(self, labels):
        "Returns a new Query whose results are any of the specified labels"
        return self._extend_query("labels", labels)
    
    def items(self):
        "Executes the query and returns the items."
        # Make sure it's a valid combination 
        filter_names = set(self.filters.keys())
        if filter_names == set():
            keys = self.redis_conn.zrange("all", 0, -1)
        elif filter_names == set(["stream"]):
            keys = self.redis_conn.zrange("stream:%s" % self.filters['stream'], 0, -1)
        elif filter_names == set(["stream", "range"]):
            keys = self.redis_conn.zrangebyscore(
                "stream:%s" % self.filters['stream'],
                self.filters['range'][0],
                self.filters['range'][1],
            )
        elif filter_names == set(["range"]):
            keys = self.redis_conn.zrangebyscore(
                "all",
                self.filters['range'][0],
                self.filters['range'][1],
            )
        else:
            raise ValueError("Invalid combination of filters: %s" % ", ".join(filter_names))
        # Iterate over the keys and return LogLine objects
        for key in keys:
            yield self._key_to_instance(key)
    
    def _key_to_instance(self, key):
        stream_name, timestamp = key.split(":", 1)
        return LogLine(self.redis_conn, stream_name, int(timestamp))

    def __iter__(self):
        return iter( self.items() )
    














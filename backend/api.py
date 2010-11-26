import datetime

class BaseQuery(object):
    """
    Very basic common shared functionality.
    """

    all_key_pattern = None

    def __init__(self, redis_conn, mission_name, filters=None):
        self.redis_conn = redis_conn
        self.mission_name = mission_name
        if filters is None:
            self.filters = {}
        else:
            self.filters = filters
        self.all_key = self.all_key_pattern % {"mission_name": mission_name} 

    def _extend_query(self, key, value):
        new_filters = dict(self.filters.items())
        new_filters[key] = value
        return self.__class__(self.redis_conn, self.mission_name, new_filters)

    def __iter__(self):
        return iter( self.items() )
    

class LogLine(object):
    """
    Basic object that represents a log line; pass in the timestamp
    and transcript name and it will extract the right bits of data and
    make them accessible via attributes.
    """
    
    def __init__(self, redis_conn, transcript_name, timestamp):
        self.redis_conn = redis_conn
        self.transcript_name = transcript_name
        self.mission_name = transcript_name.split("/")[0]
        self.timestamp = timestamp
        self.id = "%s:%i" % (self.transcript_name, self.timestamp)
        self._load()

    @classmethod
    def by_log_line_id(cls, redis_conn, log_line_id):
        transcript, timestamp = log_line_id.split(":", 1)
        timestamp = int(timestamp)
        return cls(redis_conn, transcript, timestamp)

    def _load(self):
        data = self.redis_conn.hgetall("log_line:%s:info" % self.id)
        # Load onto our attributes
        self.page = int(data['page'])
        self.transcript_page = data['transcript_page']
        self.lines = [
            [x.strip() for x in line.split(":", 1)]
            for line in self.redis_conn.lrange("log_line:%s:lines" % self.id, 0, -1)
        ]
        self.next_log_line_id = data.get('next', None)
        self.previous_log_line_id = data.get('previous', None)
        self.act_number = int(data['act'])
        self.utc_time = datetime.datetime.utcfromtimestamp(int(data['utc_time']))

    def __repr__(self):
        return "<LogLine %s:%i, page %s (%s lines)>" % (self.transcript_name, self.timestamp, self.page, len(self.lines))

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

    def next_timestamp(self):
        next_log_line = self.next()
        if next_log_line is None:
            return None
        else:
            return next_log_line.timestamp

    def previous_timestamp(self):
        previous_log_line = self.previous()
        if previous_log_line is None:
            return None
        else:
            return previous_log_line.timestamp

    def following_silence(self):
        try:
            return self.next_timestamp() - self.timestamp
        except TypeError:
            return None

    def act(self):
        return Act(self.redis_conn, self.mission_name, self.act_number)

    def images(self):
        "Returns any images associated with this LogLine."
        image_ids = self.redis_conn.lrange("log_line:%s:images" % self.id, 0, -1)
        images = [self.redis_conn.hgetall("image:%s" % id) for id in image_ids]
        return images

    class Query(BaseQuery):
        """
        Allows you to query for LogLines.
        """

        all_key_pattern = "log_lines:%(mission_name)s"

        def transcript(self, transcript_name):
            "Returns a new Query filtered by transcript"
            return self._extend_query("transcript", transcript_name)
        
        def range(self, start_time, end_time):
            "Returns a new Query whose results are between two times"
            return self._extend_query("range", (start_time, end_time))
        
        def page(self, page_number):
            "Returns a new Query whose results are all the log lines on a given page"
            return self._extend_query("page", page_number)

        def first_after(self, timestamp):
            "Returns the closest log line after the timestamp."
            if "transcript" in self.filters:
                key = "transcript:%s" % self.filters['transcript']
            else:
                key = self.all_key
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
            if "transcript" in self.filters:
                key = "transcript:%s" % self.filters['transcript']
            else:
                key = self.all_key
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

        def first(self):
            "Returns the first log line if you've filtered by page."
            if set(self.filters.keys()) == set(["transcript", "page"]):
                try:
                    key = self.redis_conn.lrange("page:%s:%i" % (self.filters['transcript'], self.filters['page']), 0, 0)[0]
                except IndexError:
                    raise ValueError("There are no log lines for this page.")
                return self._key_to_instance(key)
            else:
                raise ValueError("You can only use first() if you've used page() and transcript() only.")
        
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
                keys = self.redis_conn.zrange(self.all_key, 0, -1)
            elif filter_names == set(["transcript"]):
                keys = self.redis_conn.zrange("transcript:%s" % self.filters['transcript'], 0, -1)
            elif filter_names == set(["transcript", "range"]):
                keys = self.redis_conn.zrangebyscore(
                    "transcript:%s" % self.filters['transcript'],
                    self.filters['range'][0],
                    self.filters['range'][1],
                )
            elif filter_names == set(["range"]):
                keys = self.redis_conn.zrangebyscore(
                    self.all_key,
                    self.filters['range'][0],
                    self.filters['range'][1],
                )
            elif filter_names == set(['page', 'transcript']):
                keys = self.redis_conn.lrange("page:%s:%i" % (self.filters['transcript'], self.filters['page']), 0, -1)
            else:
                raise ValueError("Invalid combination of filters: %s" % ", ".join(filter_names))
            # Iterate over the keys and return LogLine objects
            for key in keys:
                yield self._key_to_instance(key)
        
        def _key_to_instance(self, key):
            transcript_name, timestamp = key.split(":", 1)
            return LogLine(self.redis_conn, transcript_name, int(timestamp))
    

class Act(object):
    """
    Represents an Act in the mission.
    """
    
    def __init__(self, redis_conn, mission_name, number):
        self.redis_conn = redis_conn
        self.mission_name = mission_name
        self.number = number
        self.id = "%s:%i" % (self.mission_name, self.number)
        self._load()

    def __eq__(self, other):
        return self.id == other.id

    def _load(self):
        data = self.redis_conn.hgetall("act:%s" % self.id)
        # Load onto our attributes
        self.start = int(data['start'])
        self.end = int(data['end'])
        self.title = data['title']
        self.description = data['description']
        self.data = data

    def __repr__(self):
        return "<Act %s:%i [%s to %s]>" % (self.mission_name, self.number, self.start, self.end)

    def log_lines(self):
        return LogLine.Query(self.redis_conn, self.mission_name).range(self.start, self.end)

    def includes(self, timestamp):
        return self.start <= timestamp < self.end

    class Query(BaseQuery):
        
        all_key_pattern = "acts:%(mission_name)s"

        def items(self):
            "Executes the query and returns the items."
            # Make sure it's a valid combination 
            filter_names = set(self.filters.keys())
            if filter_names == set():
                keys = self.redis_conn.lrange(self.all_key, 0, -1)
            else:
                raise ValueError("Invalid combination of filters: %s" % ", ".join(filter_names))
            # Iterate over the keys and return LogLine objects
            for key in keys:
                yield self._key_to_instance(key)

        def _key_to_instance(self, key):
            mission_name, number = key.split(":", 1)
            return Act(self.redis_conn, mission_name, int(number))

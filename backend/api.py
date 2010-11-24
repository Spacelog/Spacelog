
class LogLine(object):
    """
    Basic object that represents a log line; pass in the timestamp
    and stream name and it will extract the right bits of data and
    make them accessible via attributes.
    """
    
    def __init__(self, stream, timestamp):
        self.stream = stream
        self.timestamp = timestamp

    @classmethod
    def by_log_line_id(cls, log_line_id):
        stream, timestamp = log_line_id.split(":", 1)
        timestamp = int(timestamp)
        return cls(stream, timestamp)
    

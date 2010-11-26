from django.views.generic import TemplateView
from backend.api import LogLine, Act
import redis

class TranscriptView(TemplateView):
    """
    Base view for all views which deal with transcripts.
    Provides some nice common functionality.
    """

    def __init__(self):
        self.redis_conn = redis.Redis()

    def parse_mission_time(self, mission_time):
        "Parses a mission timestamp from a URL and converts it to a number of seconds"
        d, h, m, s = [ int(x) for x in mission_time.split(':') ]
        return s + m*60 + h*3600 + d*86400

    def log_line_query(self):
        return LogLine.Query(self.redis_conn, 'a13')

    def act_query(self):
        return Act.Query(self.redis_conn, 'a13')

    def log_lines(self, start_page, end_page):
        "Returns the log lines and the previous/next timestamps"
        # Collect the log lines
        log_lines = []
        for page in range(start_page, end_page+1):
            log_lines = list(self.log_line_query().transcript('a13/TEC').page(page))
        # Find the previous log line from this, and then the beginning of its page
        try:
            previous_timestamp = self.log_line_query().transcript('a13/TEC').page(start_page - 1).first().timestamp
        except ValueError:
            previous_timestamp = None
        # Find the next log line and its timestamp
        next_log_line = log_lines[-1].next()
        if next_log_line:
            next_timestamp = next_log_line.timestamp
        else:
            next_timestamp = None
        # Return
        return log_lines, previous_timestamp, next_timestamp

    def page_number(self, timestamp):
        "Finds the page number for a given timestamp"
        acts = list(self.act_query().items())
        if timestamp is None:
            timestamp = acts[0].start
        else:
            timestamp = self.parse_mission_time(timestamp)
        closest_log_line = self.log_line_query().first_after(timestamp)
        return closest_log_line.page


class PageView(TranscriptView):
    """
    Shows a single page of transcript, based on a passed-in timestamp.
    """

    template_name = 'transcripts/page.html'

    def get_context_data(self, start=None, end=None):

        if end is None:
            end = start

        # Get the content
        log_lines, previous_timestamp, next_timestamp = self.log_lines(
            self.page_number(start),
            self.page_number(end),
        )

        return {
            'log_lines': log_lines,
            'next_timestamp': next_timestamp,
            'previous_timestamp': previous_timestamp,
            'acts': list(self.act_query().items()),
            'current_act': log_lines[0].act(),
        }


class RangeView(PageView):
    """
    Shows records between two timestamps (may also include just
    showing a single record).
    """
    
    def log_lines(self, start_page, end_page):
        log_lines, previous_link, next_link = super(RangeView, self).log_lines(start_page, end_page)
        start = self.parse_mission_time(self.kwargs['start'])
        end = self.parse_mission_time(self.kwargs.get('end', self.kwargs['start']))
        for log_line in log_lines:
            if start <= log_line.timestamp <= end:
                log_line.highlighted = True
        return log_lines, previous_link, next_link


class PhasesView(TranscriptView):
    """
    Shows the list of all phases (acts).
    """
    
    template_name = 'transcripts/phases.html'
    
    def get_context_data(self):
        redis_conn = redis.Redis()
        return {
            'acts': list(self.act_query().items()),
        }


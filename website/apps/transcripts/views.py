from django.http import Http404
from django.views.generic import TemplateView
from website.apps.common.template import JsonTemplateView
from backend.api import LogLine, Act
from backend.util import timestamp_to_seconds
from transcripts.templatetags.linkify import linkify

class TranscriptView(JsonTemplateView):
    """
    Base view for all views which deal with transcripts.
    Provides some nice common functionality.
    """

    def parse_mission_time(self, mission_time):
        "Parses a mission timestamp from a URL and converts it to a number of seconds"
        # d, h, m, s = [ int(x) for x in mission_time.split(':') ]
        # print mission_time
        # return s + m*60 + h*3600 + d*86400
        return timestamp_to_seconds( mission_time )

    def log_line_query(self):
        return LogLine.Query(self.request.redis_conn, self.request.mission.name)

    def act_query(self):
        return Act.Query(self.request.redis_conn, self.request.mission.name)

    def main_transcript_query(self):
        return self.log_line_query().transcript(self.request.mission.main_transcript)

    def media_transcript_query(self):
        return self.log_line_query().transcript(self.request.mission.media_transcript)

    def log_lines(self, start_page, end_page):
        "Returns the log lines and the previous/next timestamps, with images mixed in."
        if end_page > (start_page + 5):
            end_page = start_page + 5
        # Collect the log lines
        log_lines = []
        done_closest = False
        for page in range(start_page, end_page+1):
            log_lines += list(self.main_transcript_query().page(page))
        for log_line in log_lines:
            log_line.images = list(log_line.images())
            log_line.lines = [
                (s, linkify(t.decode("utf8"), self.request))
                for s, t in log_line.lines
            ]
            # If this is the first after the start time, add an anchor later
            if log_line.timestamp > timestamp_to_seconds(self.kwargs.get('start', "00:00:00:00")) and not done_closest:
                log_line.closest = True
                done_closest = True
        # Find all media that falls inside this same range, and add it onto the preceding line.
        for image_line in self.media_transcript_query().range(log_lines[0].timestamp, log_lines[-1].timestamp):
            # Find the line just before the images
            last_line = None
            for log_line in log_lines:
                if log_line.timestamp > image_line.timestamp:
                    break
                last_line = log_line
            # Add the images to it
            last_line.images += image_line.images()
        # Find the previous log line from this, and then the beginning of its page
        try:
            previous_timestamp = self.main_transcript_query().page(start_page - 1).first().timestamp
        except ValueError:
            previous_timestamp = None
        # Find the next log line and its timestamp
        next_timestamp = log_lines[-1].next_timestamp()
        # Return
        return log_lines, previous_timestamp, next_timestamp, 0, None

    def page_number(self, timestamp):
        "Finds the page number for a given timestamp"
        acts = list(self.act_query().items())
        if timestamp is None:
            timestamp = acts[0].start
        else:
            timestamp = self.parse_mission_time(timestamp)
        try:
            closest_log_line = self.main_transcript_query().first_after(timestamp)
        except ValueError:
            raise Http404("No log entries match that timestamp.")
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
        log_lines, previous_timestamp, next_timestamp, max_highlight_index, first_highlighted_line = self.log_lines(
            self.page_number(start),
            self.page_number(end),
        )
        
        act          = log_lines[0].act()
        act_id       = log_lines[0].act().number
        acts         = list(self.act_query().items())
        previous_act = None
        next_act     = None
        
        if act_id > 0:
            previous_act = acts[act_id-1]
        if act_id < len(acts) - 1:
            next_act = acts[act_id+1]
        
        for log_line in log_lines:
            if log_line.transcript_page:
                original_transcript_page = log_line.transcript_page
                break
        else:
            original_transcript_page = None
        
        return {
            'log_lines': log_lines,
            'next_timestamp': next_timestamp,
            'previous_timestamp': previous_timestamp,
            'acts': acts,
            'act': act_id+1,
            'current_act': act,
            'previous_act': previous_act,
            'next_act': next_act,
            'max_highlight_index': max_highlight_index,
            'first_highlighted_line': first_highlighted_line,
            'original_transcript_page': original_transcript_page,
            'permalink': 'http://%s%s%s' % (
                self.request.META['HTTP_HOST'],
                self.request.path,
                '#show-selection',
            )
        }


class RangeView(PageView):
    """
    Shows records between two timestamps (may also include just
    showing a single record).
    """
    
    def log_lines(self, start_page, end_page):
        log_lines, previous_link, next_link, highlight_index, discard = super(RangeView, self).log_lines(start_page, end_page)
        start = self.parse_mission_time(self.kwargs['start'])
        # If there's no end, make it the first item after the given start.
        if "end" in self.kwargs:
            end = self.parse_mission_time(self.kwargs['end'])
        else:
            end = self.main_transcript_query().first_after(start).timestamp

        highlight_index = 0
        first_highlighted_line = None
        for log_line in log_lines:
            if start <= log_line.timestamp <= end:
                log_line.highlighted = True
                if highlight_index == 0:
                    first_highlighted_line = log_line
                highlight_index += 1
                log_line.highlight_index = highlight_index

        for log_line1, log_line2 in zip(log_lines, log_lines[1:]):
            if getattr(log_line2, 'highlight_index', None) == 1:
                log_line1.pre_highlight = True
                break

        return log_lines, previous_link, next_link, highlight_index, first_highlighted_line

    def get_context_data(self, start=None, end=None):
        data = super(RangeView, self).get_context_data(start, end)
        data.update({
            "selection_start_timestamp": self.parse_mission_time(start),
            "selection_end_timestamp": self.parse_mission_time(start if end is None else end),
        })
        return data


class PhasesView(TranscriptView):
    """
    Shows the list of all phases (acts).
    """
    
    template_name = 'transcripts/phases.html'
    
    def get_context_data(self, phase_number='1'):
        try:
            selected_act = Act(self.request.redis_conn, self.request.mission.name, int(phase_number) - 1)
        except KeyError:
            raise Http404('Phase %s not found' % phase_number)

        return {
            'acts': list(self.act_query()),
            'act': selected_act,
        }

class ErrorView(TemplateView):

    template_name = "error.html"
    error_code = 404

    default_titles = {
        404: "Page Not Found",
        500: "Server Error",
    }

    def get_context_data(self):
        error_info = self.request.redis_conn.hgetall(
            "error_page:%s:%i" % (
                self.request.mission.name,
                self.error_code,
            ),
        )
        if not error_info:
            error_info = {}
        return {
            "title": error_info.get('title', self.default_titles[self.error_code]),
            "heading": error_info.get('heading', self.default_titles[self.error_code]),
            "heading_quote": error_info.get('heading_quote', None),
            "subheading": error_info.get('subheading', ""),
            "text": error_info.get('text', ''),
            "classic_moment": error_info.get('classic_moment', None),
            "classic_moment_quote": error_info.get('classic_moment_quote', None),
        }

class OriginalView(TemplateView):

    template_name = "transcripts/original.html"

    def get_context_data(self, page):
        page = int(page)
        return {
            "page": page,
            "next_page": page + 1,
            "previous_page": page - 1 if page > 1 else None
        }

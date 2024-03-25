
import os.path
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView
from django.views.decorators.http import condition
from django.core.urlresolvers import reverse
from website.apps.common.views import JsonTemplateView
from backend.api import LogLine, Act
from backend.util import timestamp_to_seconds
from transcripts.templatetags.linkify import linkify
from transcripts.templatetags.missiontime import timestamp_to_url, selection_url
from common.views import MemorialMixin

class TranscriptView(MemorialMixin, JsonTemplateView):
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

    def get_transcript_name(self):
      if self.kwargs.get("transcript", None):
          return self.request.mission.name + "/" + self.kwargs["transcript"]
      return self.request.mission.main_transcript

    def main_transcript_query(self):
        return self.log_line_query().transcript(self.get_transcript_name())

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
                (s, linkify(t, self.request))
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

    def other_transcripts(self, start, end):
        """
        Return the list of transcripts and if they have any messages between the times specified.
        """
        for transcript in self.request.mission.transcripts:
            yield transcript, self.log_line_query().transcript(transcript).range(start, end).count()


class PageView(TranscriptView):
    """
    Shows a single page of transcript, based on a passed-in timestamp.
    """

    template_name = 'transcripts/page.html'
    
    def render_to_response(self, context):
        # Ensure that the request is always redirected to:
        # - The first page (timestampless)
        # - The timestamp for the start of an act
        # - The timestamp for the start of an in-act page
        # If the timestamp is already one of these, render as normal
        
        requested_start       = None
        if context['start']:
            requested_start   = timestamp_to_seconds( context['start'] )
        current_act           = context['current_act']
        first_log_line        = context['log_lines'][0]
        prior_log_line        = first_log_line.previous()
        
        # NOTE: is_act_first_page will be false for first act:
        #       that's handled by is_first_page
        is_first_page         = not prior_log_line
        is_act_first_page     = False
        if prior_log_line:
            is_act_first_page = prior_log_line.timestamp < current_act.start \
                             <= first_log_line.timestamp
        
        page_start_url = None
        # If we're on the first page, but have a timestamp,
        # redirect to the bare page URL
        if requested_start and is_first_page:
            if context['transcript_name'] != context['mission_main_transcript']:
                # Split transcript name from [mission]/[transcript]
                transcript = context['transcript_name'].split('/')[1]
                page_start_url = reverse("view_page", kwargs={"transcript": transcript})
            else:
                page_start_url = reverse("view_page")
        # If we're on the first page of an act,
        # but not on the act-start timestamp, redirect to that
        elif is_act_first_page \
        and requested_start != current_act.start:
            page_start_url = timestamp_to_url( context, current_act.start )
        # If we're on any other page and the timestamp doesn't match
        # the timestamp of the first item, redirect to that item's timestamp
        elif requested_start and not is_act_first_page \
        and requested_start != first_log_line.timestamp:
            page_start_url = timestamp_to_url(
                context,
                first_log_line.timestamp
            )
        
        # Redirect to the URL we found
        if page_start_url:
            if self.request.GET:
                page_start_url += '?%s' % self.request.GET.urlencode()
            return HttpResponseRedirect( page_start_url )
        
        return super( PageView, self ).render_to_response( context )
    
    def get_context_data(self, start=None, end=None, transcript=None):

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
        
        if start:
            permalink_fragment = '#log-line-%s' % timestamp_to_seconds(start)
        else:
            permalink_fragment = '#log-line-%s' % log_lines[0].timestamp
        
        return {
            # HACK: Force request into context. Not sure why it's not here.
            'request': self.request,
            'mission_name': self.request.mission.name,
            'mission_main_transcript': self.request.mission.main_transcript,
            'transcript_name': self.get_transcript_name(),
            'transcript_short_name': self.get_transcript_name().split('/')[1],
            'start' : start,
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
                self.request.get_host(),
                self.request.path,
                permalink_fragment,
            ),
            'other_transcripts': self.other_transcripts(
                log_lines[0].timestamp,
                log_lines[-1].timestamp,
            ),
        }


class RangeView(PageView):
    """
    Shows records between two timestamps (may also include just
    showing a single record).
    """
    
    def render_to_response(self, context):
        # Identify whether our start and end timestamps match real timestamps
        # If not, redirect from the invalid-timestamped URL to the
        # URL with timestamps matching loglines
        start = context['selection_start_timestamp']
        end = context['selection_end_timestamp']
        if start == end:
            end = None
        
        start_line = context['first_highlighted_line']
        
        # Find the last log_line in the current selection if we have a range
        end_line = start_line
        if end:
            for log_line in context['log_lines']:
                if end_line.timestamp <= log_line.timestamp <= end:
                    end_line = log_line
                elif end <= log_line.timestamp:
                    break
        
        # Get the URL we should redirect to (if any)
        page_start_url = None
        if (not end and start != start_line.timestamp) \
        or (end and start != end and start_line.timestamp == end_line.timestamp):
            # We have an individual start time only
            # -or-
            # We have start and end times that resolve to the same log_line
            page_start_url = selection_url( context, start_line.timestamp )
        elif (start != start_line.timestamp) \
          or (end and end != end_line.timestamp):
            # We have an invalid start/end time in a range
            # Doesn't matter if start is valid or not: this will handle both
            page_start_url = selection_url(
                context,
                start_line.timestamp,
                end_line.timestamp
            )
        
        # Redirect to the URL we found
        if page_start_url:
            return HttpResponseRedirect( page_start_url )
            
        return super( PageView, self ).render_to_response( context )
    
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

    def get_context_data(self, start=None, end=None, transcript=None):
        data = super(RangeView, self).get_context_data(start, end, transcript)
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

class ErrorView(MemorialMixin, TemplateView):

    template_name = "error.html"
    error_code = 404

    default_titles = {
        404: "Page Not Found",
        500: "Server Error",
    }

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
        response_kwargs.update({ "status": self.error_code })
        return super(ErrorView, self).render_to_response(context, **response_kwargs)

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

class OriginalView(MemorialMixin, TemplateView):

    template_name = "transcripts/original.html"
    
    def get_transcript_name(self):
      if self.kwargs.get("transcript", None):
          return self.request.mission.name + "/" + self.kwargs["transcript"]
      return self.request.mission.main_transcript
    
    def get_context_data(self, page, transcript=None):
        page = int(page)
        transcript_name = self.get_transcript_name();
        max_transcript_pages = int(self.request.mission.transcript_pages[transcript_name])
        
        if not 1 <= page <= max_transcript_pages:
            raise Http404("No original page with that page number.")
        
        return {
            'transcript_name': transcript_name,
            'transcript_short_name': transcript_name.split('/')[1],
            "page": page,
            "next_page": page + 1 if page < max_transcript_pages else None,
            "previous_page": page - 1 if page > 1 else None,
            "first_log_line": self.first_log_line(),
        }

    def first_log_line(self):
        try:
            return next(self.log_lines())
        except StopIteration:
            return None

    def log_lines(self):
        return list(self.transcript_query().transcript_page(self.page).items())

    def transcript_query(self):
        return self.log_line_query().transcript(self.get_transcript_name())

    def log_line_query(self):
        return LogLine.Query(self.request.redis_conn, self.request.mission.name)

    @property
    def page(self):
        return self.kwargs["page"]


class ProgressiveFileWrapper(object):
    def __init__(self, filelike, blksize, interval):
        self.filelike = filelike
        self.blksize = blksize
        self.lastsend = None
        if hasattr(filelike,'close'):
            self.close = filelike.close

    def _wait(self):
        if self.lastsend is None:
            return
        diff = time() - self.lastsend + interval
        if diff < 0:
            return
        sleep(diff)

    def __getitem__(self,key):
        self._wait()
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise IndexError

    def __iter__(self):
        return self

    def __next__(self):
        self._wait()
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise StopIteration

@condition(etag_func=None)
def stream(request, start):
    bitrate = 48000
    offset = 555
    file_path = os.path.join(settings.SITE_ROOT, '../missions/mr3/audio/ATG.mp3')
    start = timestamp_to_seconds(start)
    offset = int((start + offset) * bitrate / 8)
    file_size = os.path.getsize(file_path)
    if offset > file_size or offset < 0:
        raise Http404
    fh = open(file_path, 'r')
    fh.seek(offset)
    response = HttpResponse(ProgressiveFileWrapper(fh, int(bitrate / 8), 1))
    response['Content-Type'] = 'audio/mpeg'
    return response

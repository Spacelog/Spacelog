import os.path
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from website.apps.common.views import JsonTemplateView
from backend.api import LogLine, Act
from backend.util import timestamp_to_seconds
from transcripts.templatetags.linkify import linkify
from transcripts.templatetags.missiontime import timestamp_to_url, selection_url

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

    def transcript_query(self, transcript):
        return self.log_line_query().transcript(transcript)

    def log_lines(self, start_page, end_page, transcript):
        "Returns the log lines and the previous/next timestamps, with images mixed in."

        if end_page > (start_page + 5):
            end_page = start_page + 5
        # Collect the log lines
        log_lines = []
        done_closest = False
        
        assert self.request.redis_conn.exists("page:%s:%s" % (transcript, start_page))
        
        for page in range(start_page, end_page+1):
            log_lines += list(self.transcript_query(transcript).page(page))
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
        if transcript==self.request.mission.main_transcript:
            for image_line in self.transcript_query(self.request.mission.media_transcript).range(log_lines[0].timestamp, log_lines[-1].timestamp):
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
            previous_timestamp = self.transcript_query(transcript).page(start_page - 1).first().timestamp
        except ValueError:
            previous_timestamp = None
        # Find the next log line and its timestamp
        next_timestamp = log_lines[-1].next_timestamp()
        # Return
        return log_lines, previous_timestamp, next_timestamp, 0, None

    def page_number(self, timestamp, transcript):
        "Finds the page number for a given timestamp and transcript"
        acts = list(self.act_query().items())
        if timestamp is None:
            timestamp = acts[0].start
        else:
            timestamp = self.parse_mission_time(timestamp)
        try:
            closest_log_line = self.transcript_query(transcript).first_after(timestamp)
        except ValueError:
            raise Http404("No log entries match that timestamp.")
        return closest_log_line.page


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
        # next line is complicated. log_lines is a list of (timestamp, stuff) tuples
        # where stuff is a tuple of (transcript, line) tuples. The first transcript
        # in each stuff tuple is always the "view" transcript, and is guaranteed to
        # have something at the first timestamp that happens in this range/page, thus
        # we can get:
        #
        #  context['log_lines'][0]          -- first (timestamp, stuff) tuple
        #  context['log_lines'][0][1]       -- stuff
        #  context['log_lines'][0][1][0]    -- (transcript, line) for view transcript
        #  context['log_lines'][0][1][0][0] -- first line for view transcript
        first_log_line        = context['log_lines'][0][1][0][1]
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
            page_start_url = reverse("view_page")
        # If we're on the first page of an act,
        # but not on the act-start timestamp, redirect to that
        elif is_act_first_page \
        and requested_start != current_act.start:
            page_start_url = timestamp_to_url( current_act.start )
        # If we're on any other page and the timestamp doesn't match
        # the timestamp of the first item, redirect to that item's timestamp
        elif requested_start and not is_act_first_page \
        and requested_start != first_log_line.timestamp:
            page_start_url = timestamp_to_url(
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
        if transcript:
            transcript = "%s/%s" % (self.request.mission.name, transcript)
        else:
            transcript = self.request.mission.main_transcript

        # Get the content
        log_lines, previous_timestamp, next_timestamp, max_highlight_index, first_highlighted_line = self.log_lines(
            self.page_number(start, transcript),
            self.page_number(end, transcript),
            transcript,
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

        if transcript != self.request.mission.main_transcript:
            out_log_lines = []
            second_log_lines = list(self.transcript_query(self.request.mission.main_transcript).range(
                log_lines[0].timestamp,
                next_timestamp,
            ))
            main_idx = 0
            second_idx = 0
            current = None
            main_transcript = transcript
            second_transcript = self.request.mission.main_transcript
            while main_idx < len(log_lines) or second_idx < len(second_log_lines):
                main_ts = log_lines[main_idx].timestamp if main_idx < len(log_lines) else None
                second_ts = second_log_lines[second_idx].timestamp if second_idx < len(second_log_lines) else None
                if main_ts==second_ts:
                    # add a tuple with both
                    out_log_lines.append(
                        [
                            main_ts,
                            (
                                ( main_transcript, log_lines[main_idx] ),
                                ( second_transcript, second_log_lines[second_idx] ),
                            ),
                        ]
                    )
                    main_idx += 1
                    second_idx += 1
                elif (main_ts < second_ts and main_ts is not None) or second_ts is None:
                    out_log_lines.append(
                        [
                            main_ts,
                            (
                                ( main_transcript, log_lines[main_idx] ),
                                ( second_transcript, None ),
                            ),
                        ]
                    )
                    main_idx += 1
                elif (second_ts < main_ts and second_ts is not None) or main_ts is None:
                    # main_ts > second_ts:
                    out_log_lines.append(
                        [
                            main_ts,
                            (
                                ( main_transcript, None ),
                                ( second_transcript, second_log_lines[second_idx] ),
                            ),
                        ]
                    )
                    second_idx += 1
        else:
            out_log_lines = map(lambda x: [ x.timestamp, ( ( transcript, x ), ) ], log_lines)
        
        return {
            'start' : start,
            'log_lines': out_log_lines,
            'next_timestamp': next_timestamp,
            'transcript': transcript,
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
                permalink_fragment,
            )
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
            page_start_url = selection_url( start_line.timestamp )
        elif (start != start_line.timestamp) \
          or (end and end != end_line.timestamp):
            # We have an invalid start/end time in a range
            # Doesn't matter if start is valid or not: this will handle both
            page_start_url = selection_url(
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

    def render_to_response(self, context):
        """
        Returns a response with a template rendered with the given context.
        """
        return self.get_response(self.render_template(context), status=self.error_code)

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
        # FIXME: You can scroll off the end of the transcript, but we
        # don't have the .png files locally to check that now.
        return {
            "page": page,
            "next_page": page + 1,
            "previous_page": page - 1 if page > 1 else None,
        }

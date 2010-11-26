import os
from django.views.generic import TemplateView
from django.conf import settings
from django.utils.safestring import mark_safe
import xappy
import redis
from backend.api import LogLine

class SearchView(TemplateView):

    template_name = 'search/results.html'

    def get_context_data(self):
        # Get the query text
        q = self.request.GET.get('q', '')
        # Get the offset value
        try:
            offset = int(
                self.request.GET.get('offset', '0')
            )
        except ValueError:
            offset = 0
        # Get the results from Xapian
        db = xappy.SearchConnection(
            os.path.join(
                settings.SITE_ROOT,
                '..',
                "xappydb",
            ),
        )
        results = db.search(
            query=db.query_parse(
                q,
                default_op=db.OP_OR
            ),
            startrank=offset,
            endrank=offset+20, # FIXME: magic number
        )
        # Go through the results, building a list of LogLine objects
        redis_conn = redis.Redis()
        log_lines = []
        for result in results:
            transcript_name, timestamp = result.id.split(":", 1)
            log_line = LogLine(redis_conn, transcript_name, int(timestamp))
            log_line.speaker = result.data['speaker'][0]
            log_line.summary = mark_safe(result.summarise("text", maxlen=100, ellipsis='&hellip;', hl=('<em>', '</em>')))
            log_lines.append(log_line)

        # FIXME: db.close()
        
        return {
            'log_lines': log_lines,
            'q': q,
            'offset': offset,
        }

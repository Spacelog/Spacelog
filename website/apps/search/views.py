import os
import urllib
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
import xappy
import redis
from backend.api import LogLine

PAGESIZE = 20

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
            if offset < 0:
                offset = 0
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
            endrank=offset+PAGESIZE,
            checkatleast=offset+PAGESIZE+1,
        )
        # Go through the results, building a list of LogLine objects
        redis_conn = redis.Redis()
        log_lines = []
        for result in results:
            transcript_name, timestamp = result.id.split(":", 1)
            log_line = LogLine(redis_conn, transcript_name, int(timestamp))
            log_line.speaker = result.data['speaker'][0]
            log_line.title = mark_safe(log_line.speaker + ": &ldquo;" + result.summarise("text", maxlen=50, ellipsis='&hellip;', strict_length=True, hl=None)) + "&rdquo;"
            log_line.summary = mark_safe(result.summarise("text", maxlen=600, ellipsis='&hellip;', hl=('<em>', '</em>')))
            log_lines.append(log_line)

        def page_url(offset):
            return reverse("search") + '?' + urllib.urlencode({
                'q': q,
                'offset': offset,
            })

        if offset==0:
            previous_page = False
        else:
            previous_page = page_url(offset - PAGESIZE)

        if offset+PAGESIZE > results.matches_estimated:
            next_page = False
        else:
            next_page = page_url(offset + PAGESIZE)

        thispage = offset / PAGESIZE
        maxpage = results.matches_estimated / PAGESIZE
        
        pages_to_show = set([1]) | set([thispage-1, thispage, thispage+1]) | set([maxpage])
        if 0 == thispage:
            pages_to_show.remove(thispage-1)
        if maxpage == thispage:
            pages_to_show.remove(thispage+1)
        pages = []
        
        class Page(object):
            def __init__(self, number, url, selected=False):
                self.number = number
                self.url = url
                self.selected = selected
        
        for page in pages_to_show:
            if len(pages)>1 and page != pages[-1].number:
                pages.append('...')
            pages.append(Page(page+1, page_url(page*PAGESIZE), page==thispage))
        
        return {
            'log_lines': log_lines,
            'result': results,
            'q': q,
            'previous_page': previous_page,
            'next_page': next_page,
            'pages': pages,
        }

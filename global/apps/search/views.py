import os
import urllib
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
import xappy
import xapian
import redis
from backend.api import LogLine, Character

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

        # Is it a special search?
        redis_conn = redis.Redis()
        special_value = redis_conn.get("special_search:%s" % q)
        if special_value:
            self.template_name = "search/special.html"
            return {
                "q": q,
                "text": special_value,
            }

        # Get the results from Xapian
        db = xappy.SearchConnection(
            os.path.join(
                settings.SITE_ROOT,
                '..',
                "xappydb",
            ),
        )
        query = db.query_parse(
            q,
            default_op=db.OP_OR,
            deny = [ "mission" ],
        )
        # query=db.query_filter(
        #     query,
        #     db.query_field("mission", self.request.mission.name),
        # )
        results = db.search(
            query=query,
            startrank=offset,
            endrank=offset+PAGESIZE,
            checkatleast=offset+PAGESIZE+1,
        )
        # Go through the results, building a list of LogLine objects
        log_lines = []
        for result in results:
            transcript_name, timestamp = result.id.split(":", 1)
            log_line = LogLine(redis_conn, transcript_name, int(timestamp))
            log_line.speaker = Character(redis_conn, transcript_name.split('/')[0], result.data['speaker'][0])
            log_line.title = mark_safe(result.summarise("text", maxlen=50, ellipsis='&hellip;', strict_length=True, hl=None))
            log_line.summary = mark_safe(result.summarise("text", maxlen=600, ellipsis='&hellip;', hl=('<mark>', '</mark>')))
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
        
        pages_to_show = set([0]) | set([thispage-1, thispage, thispage+1]) | set([maxpage])
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
        
        pages_in_order = list(pages_to_show)
        pages_in_order.sort()
        for page in pages_in_order:
            if len(pages)>0 and page != pages[-1].number:
                pages.append('...')
            pages.append(Page(page+1, page_url(page*PAGESIZE), page==thispage))
        
        return {
            'log_lines': log_lines,
            'result': results,
            'q': q,
            'previous_page': previous_page,
            'next_page': next_page,
            'pages': pages,
            'debug': {
                'query': query,
            },
        }

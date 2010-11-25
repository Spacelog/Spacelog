from django.shortcuts import render_to_response
from django.views.generic import TemplateView
from backend.api import LogLine
import redis

class PageView(TemplateView):

    template_name = 'transcripts/page.html'

    def get_context_data(self, timestamp=-10):
        redis_conn = redis.Redis()

        closest_log_line = LogLine.Query(redis_conn, 'a13').first_after(int(timestamp))
        print closest_log_line
        page_number = closest_log_line.page

        return {
            'page_number': page_number,
            'log_lines': LogLine.Query(redis_conn, 'a13').transcript('a13/TEC').page(page_number),
        }


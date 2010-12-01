from django.template.loader import render_to_string
from django.views.generic import TemplateView
from backend.util import timestamp_to_seconds
from backend.api import LogLine, Act
from website.apps.common.views import JsonMixin

class HomepageView(TemplateView):
    template_name = 'homepage/homepage.html'
    def get_quote(self):
        quote_timestamp = self.request.redis_conn.srandmember(
            "mission:%s:homepage_quotes" % self.request.mission.name,
        )
        if quote_timestamp:
            return LogLine(
                self.request.redis_conn,
                self.request.mission.main_transcript,
                int(timestamp_to_seconds(quote_timestamp)),
            )

    def get_context_data(self):
        acts = [
            (x+1, act)
            for x, act in
            enumerate(Act.Query(self.request.redis_conn, self.request.mission.name))
        ]
        return {
            "acts": acts,
            "quote": self.get_quote(),
        }

class HomepageQuoteView(JsonMixin, HomepageView):
    def get_context_data(self):
        return {
            'quote': render_to_string('homepage/_quote.html', {'quote': self.get_quote()})
        }

        
class AboutView(TemplateView):
    template_name = 'homepage/about.html'

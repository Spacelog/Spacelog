from django.template.loader import render_to_string
from django.views.generic import TemplateView
from backend.util import timestamp_to_seconds
from backend.api import LogLine, Act
from website.apps.common.views import JsonMixin, MemorialMixin
from website.apps.people.views import mission_people

class HomepageView(TemplateView):
    def get_template_names(self):
        if self.request.mission.memorial:
            return [ 'homepage/memorial.html' ]
        else:
            return [ 'homepage/homepage.html' ]

    def get_quote(self):
        if self.request.mission.memorial:
            return None
        quote_timestamp = self.request.redis_conn.srandmember(
            "mission:%s:homepage_quotes" % self.request.mission.name,
        )
        if quote_timestamp:
            if '/' in quote_timestamp:
                transcript, timestamp = quote_timestamp.rsplit('/', 1)
                transcript = "%s/%s" % (self.request.mission.name, transcript)
            else:
                transcript = self.request.mission.main_transcript
                timestamp = quote_timestamp
            return LogLine(
                self.request.redis_conn,
                transcript,
                int(timestamp_to_seconds(timestamp)),
            )

    def get_context_data(self):
        if self.request.mission.memorial:
            people, more_people = mission_people(self.request)
            return {
                'people': [group for group in people if group['view']=='full'],
            }

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
            'quote': render_to_string(
                'homepage/_quote.html',
                { 'quote': self.get_quote() },
                request=self.request,
            )
        }

        
class AboutView(MemorialMixin, TemplateView):
    template_name = 'homepage/about.html'

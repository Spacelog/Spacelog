from django.views.generic import TemplateView
from backend.util import timestamp_to_seconds
from backend.api import LogLine, Act

class HomepageView(TemplateView):
    template_name = 'homepage/homepage.html'

    def get_context_data(self):
        acts = [
            (x+1, act)
            for x, act in
            enumerate(Act.Query(self.request.redis_conn, self.request.mission.name))
        ]
        quote_timestamp = self.request.redis_conn.srandmember(
            "mission:%s:homepage_quotes" % self.request.mission.name,
        )
        if quote_timestamp:
            quote = LogLine(
                self.request.redis_conn,
                self.request.mission.main_transcript,
                int(timestamp_to_seconds(quote_timestamp)),
            )
        else:
            quote = None
        return {
            "acts": acts,
            "quote": quote,
        }
        
class AboutView(TemplateView):
    template_name = 'homepage/about.html'

    def get_context_data(self):
        return {
            "cleaners": [
                "Ryan Alexander",
                "James Aylett",
                "George Brocklehurst",
                "David Brownlee",
                "Ben Firshman",
                "Mark Norman Francis",
                "Russ Garrett",
                "Andrew Godwin",
                "Steve Marshall",
                "Matt Ogle",
            ],
        }

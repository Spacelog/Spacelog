from django.views.generic import TemplateView
from common.views import MemorialMixin
from backend.api import Glossary


class GlossaryView(TemplateView, MemorialMixin):
    template_name = 'glossary/glossary.html'

    def get_context_data(self, **kwargs):
        return { 'terms': self._terms }

    @property
    def _terms(self):
        return sorted(
            list(self._query.items()),
            key=lambda term: term.abbr,
        )

    @property
    def _query(self):
        return Glossary.Query(self.request.redis_conn, self.request.mission.name)

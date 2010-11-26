import os
from django.views.generic import TemplateView
from django.conf import settings
import xappy

class SearchView(TemplateView):

    template_name = 'search/results.html'

    def get_context_data(self):
        q = self.request.GET.get('q', '')
        try:
            offset = int(
                self.request.GET.get('offset', '0')
            )
        except ValueError:
            offset = 0
        
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

        # FIXME: db.close()
        
        return {
            'results': results,
            'q': q,
            'offset': 0,
        }

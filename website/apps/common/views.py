from django.template.response import TemplateResponse
from django.utils import simplejson
from django.views.generic import TemplateView
from website.apps.common.response import JsonTemplateResponse


class JsonTemplateView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        if 'json' in self.request.GET:
            return self.render_to_json_response(context, **response_kwargs)
        else:
            return super(JsonTemplateView, self).render_to_response(context, **response_kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        if 'mimetype' not in response_kwargs:
            response_kwargs['mimetype'] = 'application/json'
        return JsonTemplateResponse(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            **response_kwargs
        )


class JsonMixin(object):
    def render_to_response(self, context=None):
        return self.get_response(simplejson.dumps(context), mimetype='application/json')


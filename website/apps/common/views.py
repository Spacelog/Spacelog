from django.template import loader, TemplateDoesNotExist
from django.utils import simplejson
from django.views.generic import TemplateView
from website.apps.common.template import JsonTemplate


class JsonTemplateView(TemplateView):
    """
    A template view that outputs templates as JSON for ajax requests.
    """
    def load_template(self, names):
        if 'json' not in self.request.GET:
            return super(JsonTemplateView, self).load_template(names)
        
        for name in names:
            try:
                template, origin = loader.find_template(name)
            except TemplateDoesNotExist:
                continue
            if not hasattr(template, 'render'):
                return JsonTemplate(template, origin, name)
            else:
                # do some monkey business if the template has already been
                # compiled
                new_template = JsonTemplate('', origin, name)
                new_template.nodelist = template.nodelist
                return new_template
        raise TemplateDoesNotExist(', '.join(names))

    def get_response(self, content, **httpresponse_kwargs):
        if 'json' in self.request.GET and 'mimetype' not in httpresponse_kwargs:
            httpresponse_kwargs['mimetype'] = 'application/json'
        return super(JsonTemplateView, self).get_response(content, **httpresponse_kwargs)
            


class JsonMixin(object):
    def render_to_response(self, context=None):
        return self.get_response(simplejson.dumps(context), mimetype='application/json')


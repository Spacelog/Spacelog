from django.template import Template, Context, loader, NodeList, TemplateDoesNotExist
from django.template.loader_tags import BlockNode
from django.views.generic import TemplateView
import simplejson

class JsonTemplate(Template):
    def _render(self, context):
        output = {}
        for n in self.nodelist.get_nodes_by_type(BlockNode):
            output[n.name] = n.render(context)
        return simplejson.dumps(output)


class JsonTemplateView(TemplateView):
    """
    A template view that outputs templates as JSON for ajax requests.
    """
    def is_ajax(self):
        return self.request.is_ajax() or 'ajax' in self.request.GET

    def load_template(self, names):
        if not self.is_ajax():
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
        if self.is_ajax() and 'mimetype' not in httpresponse_kwargs:
            httpresponse_kwargs['mimetype'] = 'application/json'
        return super(JsonTemplateView, self).get_response(content, **httpresponse_kwargs)
            



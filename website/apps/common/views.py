from django.utils import simplejson

class JsonMixin(object):
    def render_to_response(self, context=None):
        return self.get_response(simplejson.dumps(context), mimetype='application/json')


from django.template import Template
from django.template.loader_tags import BlockNode
from django.utils import simplejson

class JsonTemplate(Template):
    def _render(self, context):
        output = {}
        for n in self.nodelist.get_nodes_by_type(BlockNode):
            output[n.name] = n.render(context)
        return simplejson.dumps(output)




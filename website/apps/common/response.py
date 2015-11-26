import json
from django.template.loader_tags import BlockNode
from django.template.response import TemplateResponse
from django.template.context import make_context


class JsonTemplateResponse(TemplateResponse):
    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name).template
        context = make_context(self.context_data, self._request)
        output = {}
        with context.bind_template(template):
            for n in template.nodelist.get_nodes_by_type(BlockNode):
                output[n.name] = n.render(context)
        return json.dumps(output)

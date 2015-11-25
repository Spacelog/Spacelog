import json
from django.template.loader_tags import BlockNode
from django.template.response import TemplateResponse


class JsonTemplateResponse(TemplateResponse):
    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)

        output = {}
        for n in template.nodelist.get_nodes_by_type(BlockNode):
            output[n.name] = n.render(context)
        return json.dumps(output)

from django.template import engines
import json
import unittest
from website.apps.common.response import JsonTemplateResponse

class TestJsonTemplateResponse(unittest.TestCase):
    def test_blocks(self):
        template = engines['django'].from_string("""
{% extends "blah blah" %}
{% block title %}Title!{% endblock%}
{% block content %}Blah blah content{% endblock %}
""")
        response = JsonTemplateResponse(
            request=None,
            template=template,
            context={},
        )
        response.render()

        self.assertEqual(
            json.loads(response.content),
            {
                'title': 'Title!',
                'content': 'Blah blah content',
            }
        )



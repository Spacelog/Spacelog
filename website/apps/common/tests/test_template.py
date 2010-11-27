from django import template
import simplejson
import unittest
from website.apps.common.template import JsonTemplate

class TestJsonTemplate(unittest.TestCase):
    def test_blocks(self):
        output = JsonTemplate("""
{% extends "blah blah" %}
{% block title %}Title!{% endblock%}
{% block content %}Blah blah content{% endblock %}
""").render(template.Context())

        self.assertEqual(
            simplejson.loads(output),
            {
                'title': 'Title!',
                'content': 'Blah blah content',
            }
        )



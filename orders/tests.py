from django.template import Context, Template
from django.test import TestCase


class CurrencyTemplateTagTests(TestCase):
    def test_bdt_filter_renders_without_template_syntax_error(self):
        template = Template("{% load currency %} {{ 10|bdt }}")
        rendered = template.render(Context({}))

        self.assertIn("10", rendered)

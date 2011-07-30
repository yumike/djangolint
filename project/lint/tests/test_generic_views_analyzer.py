import os
from django.test import TestCase

from ..analyzers import GenericViewsAnalyzer
from ..parsers import Parser

from .base import TESTS_ROOT


class GenericViewsAnalyzerTests(TestCase):

    def setUp(self):
        self.example_project = os.path.join(TESTS_ROOT, 'example_project')
        self.code = Parser(self.example_project).parse()
        self.analyzer = GenericViewsAnalyzer(self.code, self.example_project)

    def test_analyze(self):
        results = list(self.analyzer.analyze())
        self.assertEqual(len(results), 5)
        self.assertItemsEqual(results[0].source, [
            (5, False, ''),
            (6, False, 'def index(request):'),
            (7, True,  '    return django.views.generic.simple.direct_to_template('),
            (8, False, '        request,'),
            (9, False, "        template_name='messages/index.html')"),
        ])
        self.assertItemsEqual(results[1].source, [
            (12, False, 'def redirect(request):'),
            (13, False, '    view = django.views.generic.simple.redirect_to'),
            (14, True,  "    return view(request, url='/messages/list/')"),
            (15, False, ''),
            (16, False, ''),
        ])

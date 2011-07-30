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
            (7,  False, ''),
            (8,  False, 'def index(request):'),
            (9,  True,  '    return django.views.generic.simple.direct_to_template('),
            (10, False, '        request,'),
            (11, False, "        template_name='messages/index.html')"),
        ])
        self.assertItemsEqual(results[1].source, [
            (14, False, 'def redirect(request):'),
            (15, False, '    view = django.views.generic.simple.redirect_to'),
            (16, True,  "    return view(request, url='/messages/list/')"),
            (17, False, ''),
            (18, False, ''),
        ])

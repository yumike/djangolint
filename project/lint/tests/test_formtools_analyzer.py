import os
from django.test import TestCase

from ..analyzers.formtools import FormToolsAnalyzer
from ..parsers import Parser

from .base import TESTS_ROOT


class FormToolsAnalyzerTests(TestCase):

    def setUp(self):
        self.example_project = os.path.join(TESTS_ROOT, 'example_project')
        self.code = Parser(self.example_project).parse()
        self.analyzer = FormToolsAnalyzer(self.code, self.example_project)

    def test_analyze(self):
        results = list(self.analyzer.analyze())
        self.assertEqual(len(results), 1)
        self.assertItemsEqual(results[0].source, [
            (51, False, '    from django.contrib.formtools.utils import security_hash'),
            (52, False, '    form = MessageForm()'),
            (53, True,  '    hash = security_hash(request, form)'),
            (54, False, '    return render_to_response(\'messages/form.html\', {\'form\': form, \'hash\': hash})'),
            (55, False, ''),
        ])

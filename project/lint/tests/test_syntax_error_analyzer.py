import os
from django.test import TestCase
from .base import TESTS_ROOT

from ..analyzers.syntax_error import SyntaxErrorAnalyzer
from ..parsers import Parser


class SyntaxErrorAnalyzerTests(TestCase):

    def setUp(self):
        self.example_project = os.path.join(TESTS_ROOT, 'example_project')
        self.code = Parser(self.example_project).parse()

    def test_analyze(self):
        analyzer = SyntaxErrorAnalyzer(self.code, self.example_project)
        results = list(analyzer.analyze())
        self.assertEqual(len(results), 1)

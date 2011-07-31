import os
from django.test import TestCase

from ..analyzers.context_processors import ContextProcessorsAnalyzer
from ..parsers import Parser

from .base import TESTS_ROOT


class ContextProcessorsAnalyzerTests(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.example_project = os.path.join(TESTS_ROOT, 'example_project')
        self.code = Parser(self.example_project).parse()
        self.analyzer = ContextProcessorsAnalyzer(self.code, self.example_project)

    def test_analyze(self):
        results = list(self.analyzer.analyze())
        self.assertEqual(len(results), 3)
        self.assertItemsEqual(results[0].source, [
            (18, False, ""),
            (19, False, "TEMPLATE_CONTEXT_PROCESSORS = ("),
            (20, True,  "    'django.core.context_processors.auth',"),
            (21, False, "    'django.core.context_processors.debug',"),
            (22, False, "    'django.core.context_processors.i18n',"),
        ])
        self.assertItemsEqual(results[0].solution, [
            (18, False, ""),
            (19, False, "TEMPLATE_CONTEXT_PROCESSORS = ("),
            (20, True,  "    'django.contrib.auth.context_processors.auth',"),
            (21, False, "    'django.core.context_processors.debug',"),
            (22, False, "    'django.core.context_processors.i18n',"),
        ])

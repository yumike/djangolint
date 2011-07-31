import os
from django.test import TestCase

from ..analyzers.template_loaders import TemplateLoadersAnalyzer
from ..parsers import Parser

from .base import TESTS_ROOT


class TemplateLoadersAnalyzerTests(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.example_project = os.path.join(TESTS_ROOT, 'example_project')
        self.code = Parser(self.example_project).parse()
        self.analyzer = TemplateLoadersAnalyzer(self.code, self.example_project)

    def test_analyze(self):
        results = list(self.analyzer.analyze())
        self.assertEqual(len(results), 2)
        self.assertItemsEqual(results[0].source, [
            (29, False, ''),
            (30, False, 'TEMPLATE_LOADERS = ('),
            (31, True,  "    'django.template.loaders.filesystem.load_template_source',"),
            (32, False, "    'django.template.loaders.app_directories.load_template_source',"),
            (33, False, ')'),
        ])
        self.assertItemsEqual(results[0].solution, [
            (29, False, ''),
            (30, False, 'TEMPLATE_LOADERS = ('),
            (31, True,  "    'django.template.loaders.filesystem.Loader',"),
            (32, False, "    'django.template.loaders.app_directories.load_template_source',"),
            (33, False, ')'),
        ])

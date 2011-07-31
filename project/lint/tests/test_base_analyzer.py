import os
from django.test import TestCase
from .base import TESTS_ROOT, EXAMPLE_PROJECT_FILES

from ..analyzers.base import BaseAnalyzer
from ..parsers import Parser


class CustomAnalyzer(BaseAnalyzer):

    def analyze_file(self, filepath, code):
        yield filepath


class BaseAnalyzerTests(TestCase):

    def setUp(self):
        self.example_project = os.path.join(TESTS_ROOT, 'example_project')
        self.code_dict = Parser(self.example_project).parse()
        self.analyzer = BaseAnalyzer(self.code_dict, self.example_project)

    def test_init(self):
        self.assertEqual(self.analyzer.surround_by, 2)
        self.assertEqual(self.analyzer.code_dict, self.code_dict)
        self.assertEqual(self.analyzer.repo_path, self.example_project)

    def test_file_lines(self):
        lines = list(self.analyzer.get_file_lines('syntax_error.py', 1))
        self.assertEqual(lines, [
            (1, 'def main():'),
            (2, '    syntax error'),
            (3, ''),
        ])

        lines = list(self.analyzer.get_file_lines('syntax_error.py', 3))
        self.assertEqual(lines, [
            (1, 'def main():'),
            (2, '    syntax error'),
            (3, ''),
            (4, ''),
            (5, "if __name__ == '__main__':"),
        ])

        lines = list(self.analyzer.get_file_lines('syntax_error.py', 6))
        self.assertEqual(lines, [
            (4, ''),
            (5, "if __name__ == '__main__':"),
            (6, '    main()'),
        ])

    def test_analyze_file(self):
        with self.assertRaises(NotImplementedError):
            self.analyzer.analyze_file(*self.code_dict.items()[0])

    def test_analyze(self):
        results = CustomAnalyzer(self.code_dict, self.example_project).analyze()
        self.assertItemsEqual(list(results), EXAMPLE_PROJECT_FILES)

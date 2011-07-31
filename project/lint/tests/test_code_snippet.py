from django.test import TestCase
from ..analyzers.base import CodeSnippet


class CodeSnippetTests(TestCase):

    def test_add_line(self):
        snippet = CodeSnippet()
        snippet.add_line(1, 'first line')
        snippet.add_line(2, 'second line', important=False)
        self.assertItemsEqual(snippet, [
            (1, True, 'first line'),
            (2, False, 'second line'),
        ])

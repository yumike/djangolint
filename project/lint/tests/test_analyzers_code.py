from django.test import TestCase
from ..analyzers.base import Code


class CodeTests(TestCase):

    def test_add_line(self):
        code = Code()
        code.add_line(1, 'first line')
        code.add_line(2, 'second line', important=False)
        self.assertEqual(dict(code), {
            (1, True): 'first line',
            (2, False): 'second line',
        })

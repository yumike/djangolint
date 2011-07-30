import os
from django.test import TestCase

from ..analyzers import RenderToResponseAnalyzer
from ..parsers import Parser

from .base import TESTS_ROOT


class RenderToResponseAnalyzerTests(TestCase):

    def setUp(self):
        self.example_project = os.path.join(TESTS_ROOT, 'example_project')
        self.code = Parser(self.example_project).parse()
        self.analyzer = RenderToResponseAnalyzer(self.code, self.example_project)

    def test_analyze(self):
        results = list(self.analyzer.analyze())
        self.assertEqual(len(results), 1)
        self.assertItemsEqual(results[0].source, [
            (39, False, 'def random_message(request):'),
            (40, False, "    message = Message.objects.order_by('?')[0]"),
            (41, True,  "    return render_to_response('messages/random.html', {'message': message},"),
            (42, False, '                              context_instance=RequestContext(request))'),
            (43, False, ''),
        ])

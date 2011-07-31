import os
from django.test import TestCase

from ..analyzers.render_to_response import RenderToResponseAnalyzer
from ..parsers import Parser

from .base import TESTS_ROOT


class RenderToResponseAnalyzerTests(TestCase):

    def setUp(self):
        self.example_project = os.path.join(TESTS_ROOT, 'example_project')
        self.code = Parser(self.example_project).parse()
        self.analyzer = RenderToResponseAnalyzer(self.code, self.example_project)

    def test_analyze(self):
        results = list(self.analyzer.analyze())
        self.assertEqual(len(results), 2)
        self.assertIn("this 'render_to_response'", results[0].description)
        self.assertItemsEqual(results[0].source, [
            (39, False, 'def random_message(request):'),
            (40, False, "    message = Message.objects.order_by('?')[0]"),
            (41, True,  "    return render_to_response('messages/random.html', {'message': message},"),
            (42, True, '                              context_instance=RequestContext(request))'),
            (43, False, ''),
            (44, False, ''),
        ])
        self.assertItemsEqual(results[1].source, [
            (46, False, 'def another_random_message(request):'),
            (47, False, "    message = Message.objects.order_by('?')[0]"),
            (48, True,  "    return render_to_response('messages/random.html', {'message': message},"),
            (49, True, '                              context_instance=RequestContext(request))'),
            (50, False, ''),
            (51, False, ''),
        ])

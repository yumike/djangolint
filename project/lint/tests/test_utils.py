# -*- coding: utf-8 -*-
from django.test import TestCase
from ..utils import rst2html


class RST2HTMLTests(TestCase):

    def test_converts_rst_to_html(self):
        result = rst2html('Fix *description*.')
        self.assertEqual(result, '<p>Fix <em>description</em>.</p>\n')

    def test_handles_unicode(self):
        result = rst2html(u'Описание фикса.')
        self.assertEqual(result, u'<p>Описание фикса.</p>\n')

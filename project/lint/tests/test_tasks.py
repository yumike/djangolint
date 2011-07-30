from __future__ import with_statement

import os
import shutil

from django.test import TestCase

from ..models import Report
from ..settings import CONFIG
from ..tasks import CloningError, clone


class TasksTests(TestCase):

    def setUp(self):
        self.report1 = Report.objects.create(url='git://github.com/yumike/djangolint.git')
        self.report2 = Report.objects.create(url='example.com')

    def tearDown(self):
        shutil.rmtree(CONFIG['CLONES_ROOT'])

    def test_clone(self):
        path = clone(self.report1.url, self.report1.hash)
        self.assertTrue(os.path.exists(path))
        with self.assertRaises(CloningError):
            clone(self.report2.url, self.report2.hash)

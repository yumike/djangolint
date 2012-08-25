from __future__ import with_statement

import os
import shutil

from django.test import TestCase

from ..ghclone import CloneError, clone
from ..models import Report
from ..settings import CONFIG


class CloneTests(TestCase):

    def setUp(self):
        self.report1 = Report.objects.create(url='https://github.com/yumike/djangolint')
        self.report2 = Report.objects.create(url='https://github.com/xobb1t/notexistentrepo')
        self.report3 = Report.objects.create(url='https://github.com/mirrors/linux')

    def test_clone(self):
        with clone(self.report1.github_url) as path:
            self.assertTrue(os.path.exists(path))
        with self.assertRaises(CloneError):
            with clone(self.report2.github_url):
                pass
        with self.assertRaises(CloneError):
            with clone(self.report3.github_url):
                pass

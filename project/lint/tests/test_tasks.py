from __future__ import with_statement

import os
import shutil

from django.test import TestCase

from ..models import Report
from ..settings import CONFIG
from ..tasks import CloneError, clone


class TasksTests(TestCase):

    def setUp(self):
        self.report1 = Report.objects.create(url='https://github.com/yumike/djangolint')
        self.report2 = Report.objects.create(url='https://github.com/xobb1t/notexistentrepo')
        self.report3 = Report.objects.create(url='https://github.com/mirrors/linux')

    def tearDown(self):
        try:
            shutil.rmtree(self.report1.get_repo_path())
        except OSError:
            pass
        try:
            shutil.rmtree(self.report2.get_repo_path())
        except OSError:
            pass
        try:
            shutil.rmtree(self.report3.get_repo_path())
        except OSError:
            pass

    def test_clone(self):
        path1 = self.report1.get_repo_path()
        clone(self.report1.github_url, path1)
        self.assertTrue(os.path.exists(path1))
        with self.assertRaises(CloneError):
            clone(self.report2.github_url, self.report2.get_repo_path())
        with self.assertRaises(CloneError):
            clone(self.report3.github_url, self.report3.get_repo_path())


    def test_files_delete(self):
        path1 = self.report1.get_repo_path()
        clone(self.report1.github_url, path1)
        self.report1.stage = 'done'
        self.report1.save()
        self.assertFalse(os.path.exists(path1))
        self.report1.stage = 'whait'
        self.report1.save()
        clone(self.report1.github_url, path1)
        self.report1.error = 'error'
        self.report1.save()
        self.assertFalse(os.path.exists(path1))

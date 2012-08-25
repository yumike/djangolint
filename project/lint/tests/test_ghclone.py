from __future__ import with_statement

import errno
import os
import shutil
import mock

from django.test import TestCase

from ..ghclone import CloneError, tempdir, clone
from ..models import Report
from ..settings import CONFIG


class TempDirTests(TestCase):

    def setUp(self):
        self.makedirs_patcher = mock.patch('os.makedirs')
        self.mkdtemp_patcher = mock.patch('tempfile.mkdtemp')
        self.rmtree_patcher = mock.patch('shutil.rmtree')

        self.makedirs = self.makedirs_patcher.start()
        self.mkdtemp = self.mkdtemp_patcher.start()
        self.rmtree = self.rmtree_patcher.start()

    def tearDown(self):
        self.makedirs_patcher.stop()
        self.mkdtemp_patcher.stop()
        self.rmtree_patcher.start()

    def test_creates_temp_dir(self):
        with tempdir(root='root') as path:
            pass
        self.mkdtemp.assert_called_once_with(dir='root')
        self.assertEqual(path, self.mkdtemp.return_value)

    def test_doesnt_require_explicit_root(self):
        with tempdir() as path:
            pass
        self.mkdtemp.assert_called_once_with(dir=None)

    def test_tries_to_create_root_if_passed(self):
        with tempdir(root='root') as path:
            pass
        self.makedirs.assert_called_once_with('root')

    def test_passes_silenty_if_root_already_exists(self):
        self.makedirs.side_effect = OSError(errno.EEXIST, 'File exists', 'root')
        with tempdir(root='root') as path:
            pass

    def test_raises_oserror_if_cannot_create_root(self):
        self.makedirs.side_effect = OSError(errno.EACCES, 'Permission denied', 'root')
        with self.assertRaises(OSError):
            with tempdir(root='root') as path:
                pass

    def test_doesnt_try_to_create_root_if_isnt_passed(self):
        with tempdir() as path:
            pass
        self.assertFalse(self.makedirs.called)

    def test_removes_dir_on_the_exit(self):
        with tempdir() as path:
            self.assertFalse(self.rmtree.called)
        self.rmtree.assert_called_once_with(path)

    def test_removes_dir_if_exception_is_raised(self):
        try:
            with tempdir() as path:
                raise Exception
        except Exception:
            pass
        self.rmtree.assert_called_once_with(path)


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

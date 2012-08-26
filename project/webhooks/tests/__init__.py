import os
import mock

from django.utils import simplejson as json
from django.test import TestCase
from django.test.client import Client

from ..models import Commit
from ..utils import parse_hook_data


DIRNAME = os.path.abspath(os.path.dirname(__file__))
PAYLOAD_PATH = os.path.join(DIRNAME, 'fixtures', 'payload.json')


class HookParserTestCase(TestCase):

    def setUp(self):
        with open(PAYLOAD_PATH) as f:
            self.payload = f.read()
        self.parsed_data = parse_hook_data(json.loads(self.payload))

    def testHash(self):
        self.assertTrue('hash' in self.parsed_data.keys())
        self.assertEqual(
            self.parsed_data['hash'],
            '2e7be88382545a9dc7a05b9d2e85a7041e311075',
        )

    def testCompareUrl(self):
        self.assertTrue('compare_url' in self.parsed_data.keys())
        self.assertEqual(
            self.parsed_data['compare_url'],
            'https://github.com/xobb1t/test/compare/a90ff8353403...2e7be8838254',
        )

    def testRef(self):
        self.assertTrue('ref' in self.parsed_data.keys())
        self.assertEqual(self.parsed_data['ref'], 'refs/heads/master')

    def testCommitter(self):
        self.assertTrue('committer_name' in self.parsed_data.keys())
        self.assertEqual(self.parsed_data['committer_name'], 'Dima Kukushkin')
        self.assertTrue('committer_email' in self.parsed_data.keys())
        self.assertEqual(self.parsed_data['committer_email'],
                         'dima@kukushkin.me')

    def testRepo(self):
        self.assertTrue('repo_name' in self.parsed_data.keys())
        self.assertEqual(self.parsed_data['repo_name'], 'test')
        self.assertTrue('repo_user' in self.parsed_data.keys())
        self.assertEqual(self.parsed_data['repo_user'], 'xobb1t')

    def testMessage(self):
        self.assertTrue('message' in self.parsed_data.keys())
        self.assertEqual(self.parsed_data['message'], 'Update README.md')

    def testRepoUrl(self):
        self.assertTrue('repo_url' in self.parsed_data.keys())
        self.assertEqual(self.parsed_data['repo_url'],
                         'https://github.com/xobb1t/test')


class WebhookHandlerTestCase(TestCase):

    def setUp(self):
        with open(PAYLOAD_PATH) as f:
            self.payload = f.read()
        self.client = Client()
        self.task_patcher = mock.patch('webhooks.views.process_commit')
        self.process_commit = self.task_patcher.start()

    def testNotAllowed(self):
        response = self.client.get('/webhooks/')
        self.assertEqual(response.status_code, 405)
        response = self.client.post('/webhooks/')
        self.assertNotEqual(response.status_code, 405)

    def testBadRequest(self):
        response = self.client.post('/webhooks/')
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/webhooks/', {'payload': '{"asd": 123'})
        self.assertEqual(response.status_code, 400)

    def testResponseStatusWithPayload(self):
        response = self.client.post('/webhooks/', {'payload': self.payload})
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/webhooks/', {'payload': self.payload})
        self.assertEqual(response.status_code, 200)

    def testProcessReportCalled(self):
        self.client.post('/webhooks/', {'payload': self.payload})
        commit = Commit.objects.filter(
            hash='2e7be88382545a9dc7a05b9d2e85a7041e311075',
            repo_name='test', repo_user='xobb1t'
        ).get()
        self.process_commit.delay.assert_called_once_with(commit.pk)


class CommitSaveTestCase(TestCase):

    def setUp(self):
        self.qs = Commit.objects.filter(
            hash='2e7be88382545a9dc7a05b9d2e85a7041e311075',
            repo_name='test', repo_user='xobb1t'
        )
        with open(PAYLOAD_PATH) as f:
            self.payload = f.read()
        self.client = Client()
        self.task_patcher = mock.patch('webhooks.views.process_commit')
        self.process_commit = self.task_patcher.start()

    def testCommitCreated(self):
        with self.assertRaises(Commit.DoesNotExist):
            self.qs.get()
        self.client.post('/webhooks/', {'payload': self.payload})
        self.assertEqual(self.qs.count(), 1)

    def testCommitUnique(self):
        self.client.post('/webhooks/', {'payload': self.payload})
        self.assertEqual(self.qs.count(), 1)
        self.client.post('/webhooks/', {'payload': self.payload})
        self.assertEqual(self.qs.count(), 1)

    def testCommitData(self):
        self.client.post('/webhooks/', {'payload': self.payload})
        commit = self.qs.get()
        self.assertEqual(commit.message, 'Update README.md')
        self.assertEqual(commit.committer_name, 'Dima Kukushkin')
        self.assertEqual(commit.committer_email, 'dima@kukushkin.me')
        self.assertEqual(commit.ref, 'refs/heads/master')
        self.assertEqual(commit.repo_url, 'https://github.com/xobb1t/test')
        self.assertEqual(
            commit.compare_url,
            'https://github.com/xobb1t/test/compare/a90ff8353403...2e7be8838254'
        )

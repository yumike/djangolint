from datetime import datetime, timedelta

from django.test import TestCase

from ..models import Report, Fix
from ..settings import CONFIG


def create_fix(**kwargs):
    kwargs['line'] = 0
    kwargs['report'] = Report.objects.create(url='https://github.com/django/django')
    return Fix.objects.create(**kwargs)


class ReportTestCase(TestCase):

    def setUp(self):
        expiration_days = CONFIG['REPORT_EXPIRATION_DAYS']
        self.report1 = Report.objects.create(url='https://github.com/django/django')
        expired_datetime = datetime.now() - timedelta(days=expiration_days+1)
        self.report2 = Report.objects.create(
            url='https://github.com/yumike/djangolint', created_on=expired_datetime
        )

    def test_expired(self):
        self.assertFalse(self.report1.expired())
        self.assertTrue(self.report2.expired())

    def test_delete_expired(self):
        Report.objects.delete_expired()
        qs = Report.objects.all()

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].pk, 1)


class FixTestCase(TestCase):

    def setUp(self):
        self.fix = create_fix(description='Fix description.')

    def test_caches_description_html(self):
        self.assertEqual(self.fix.description_html, '<p>Fix description.</p>\n')

    def test_updates_description_html(self):
        self.fix.description = 'Updated fix description.'
        self.fix.save()
        self.assertEqual(self.fix.description_html, '<p>Updated fix description.</p>\n')

from datetime import datetime, timedelta

from django.test import TestCase

from ..models import Report
from ..settings import CONFIG


class ReportTestCase(TestCase):

    def setUp(self):
        expiration_days = CONFIG['REPORT_EXPIRATION_DAYS']
        self.report1 = Report.objects.create(url='http://google.com/')
        expired_datetime = datetime.now() - timedelta(days=expiration_days+1)
        self.report2 = Report.objects.create(url='http://yandex.ru/', created_on=expired_datetime)

    def tearDown(self):
        Report.objects.all().delete()

    def test_expired(self):
        self.assertFalse(self.report1.expired())
        self.assertTrue(self.report2.expired())

    def test_delete_expired(self):
        Report.objects.delete_expired()
        qs = Report.objects.all()

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].pk, 1)

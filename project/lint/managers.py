from datetime import datetime, timedelta
from django.db import models
from .settings import CONFIG


EXPIRATION_DAYS = CONFIG['REPORT_EXPIRATION_DAYS']


class ReportManager(models.Manager):

    def delete_expired(self):
        expiration_date = datetime.now() - timedelta(days=EXPIRATION_DAYS)
        expired = self.filter(created__lt=expiration_date)
        expired.delete()

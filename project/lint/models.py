import random
import time
from datetime import datetime, timedelta

from django.db import models
from django.utils.hashcompat import sha_constructor

from .managers import ReportManager
from .settings import CONFIG


STAGES = (
    ('waiting', 'Waiting'),
    ('cloning', 'Cloning'),
    ('parsing', 'Parsing'),
    ('testing', 'Testing'),
    ('done', 'Done'),
)


EXPIRATION_DAYS = CONFIG['REPORT_EXPIRATION_DAYS']


class Report(models.Model):

    created_on = models.DateTimeField(default=datetime.now)

    hash = models.CharField(unique=True, max_length=40)
    url = models.URLField()
    stage = models.CharField(max_length=10, choices=STAGES,
                             default='waiting')
    error = models.TextField(blank=True, null=True)

    objects = ReportManager()

    class Meta:
        ordering = ['-created_on']

    def __unicode__(self):
        return self.url

    def save(self, *args, **kwargs):
        if not self.hash:
            salt = sha_constructor(str(random.random())).hexdigest()[:5]
            salt += str(time.time()) + self.url
            self.hash = sha_constructor(salt).hexdigest()
        super(Report, self).save(*args, **kwargs)

    def expired(self):
        expiration_date = timedelta(days=EXPIRATION_DAYS) + self.created_on
        return datetime.now() > expiration_date


class Fix(models.Model):

    report = models.ForeignKey(Report, related_name='fixes')
    path = models.CharField(max_length=255)
    line = models.PositiveIntegerField()
    source = models.TextField()
    solution = models.TextField()

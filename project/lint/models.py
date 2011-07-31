import os
import random
import shutil
import time

from datetime import datetime, timedelta

from django.db import models
from django.dispatch import receiver
from django.utils.hashcompat import sha_constructor

from .managers import ReportManager
from .settings import CONFIG


STAGES = ('queue', 'cloning', 'parsing', 'analyzing', 'done')


EXPIRATION_DAYS = CONFIG['REPORT_EXPIRATION_DAYS']


class Report(models.Model):

    created_on = models.DateTimeField(default=datetime.now)

    hash = models.CharField(unique=True, max_length=40)
    url = models.URLField(verify_exists=False)
    stage = models.CharField(max_length=10, default='queue')
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

    def get_repo_path(self):
        if self.hash:
            return os.path.join(CONFIG['CLONES_ROOT'], self.hash)
        return None

    @models.permalink
    def get_absolute_url(self):
        return ('lint_results', (), {'hash': self.hash})


class Fix(models.Model):

    report = models.ForeignKey(Report, related_name='fixes')
    description = models.TextField()
    path = models.CharField(max_length=255)
    line = models.PositiveIntegerField()
    source = models.TextField()
    solution = models.TextField()

    class Meta:
        ordering = ['path', 'line']


@receiver(models.signals.post_save, sender=Report)
def delete_unused_repos(sender=Report, **kwargs):
    if kwargs.get('raw', False):
        return
    report = kwargs['instance']
    if report.stage == 'done' or report.error:
        path = report.get_repo_path()
        try:
            shutil.rmtree(path)
        except OSError:
            pass

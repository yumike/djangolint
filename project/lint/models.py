import os
import random
import re
import shutil
import time

from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.dispatch import receiver
from django.utils.hashcompat import sha_constructor

from .managers import ReportManager
from .settings import CONFIG
from .utils import rst2html


STAGES = ('queue', 'cloning', 'parsing', 'analyzing', 'done')
EXPIRATION_DAYS = CONFIG['REPORT_EXPIRATION_DAYS']
GITHUB_REGEXP = re.compile(r'^https:\/\/github.com\/([-\w]+\/[-.\w]+?)(?:\.git|)$')


def github_validator(value):
    if not re.match(GITHUB_REGEXP, value):
        raise ValidationError('Invalid github repo url')
    return value


class Report(models.Model):

    created_on = models.DateTimeField(default=datetime.now)

    hash = models.CharField(unique=True, max_length=40)
    url = models.URLField(
        verify_exists=False, validators=[RegexValidator(GITHUB_REGEXP)]
    )
    github_url = models.CharField(max_length=255)
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
        if not self.github_url:
            match = re.match(GITHUB_REGEXP, self.url)
            if match:
                self.github_url = match.group(1)
        super(Report, self).save(*args, **kwargs)

    def expired(self):
        expiration_date = timedelta(days=EXPIRATION_DAYS) + self.created_on
        return datetime.now() > expiration_date

    @models.permalink
    def get_absolute_url(self):
        return ('lint_results', (), {'hash': self.hash})


class Fix(models.Model):

    report = models.ForeignKey(Report, related_name='fixes')
    description = models.TextField()
    description_html = models.TextField()
    path = models.CharField(max_length=255)
    line = models.PositiveIntegerField()
    source = models.TextField()
    solution = models.TextField()

    class Meta:
        ordering = ['path', 'line']

    def save(self, *args, **kwargs):
        self.description_html = rst2html(self.description)
        super(Fix, self).save(*args, **kwargs)

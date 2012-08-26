from datetime import datetime
from django.db import models


class Commit(models.Model):

    hash = models.CharField(max_length=40)
    repo_url = models.URLField(max_length=255)
    repo_name = models.CharField(max_length=255)
    repo_user = models.CharField(max_length=255)

    ref = models.CharField(max_length=100)
    compare_url = models.URLField(max_length=255)
    committer_name = models.CharField(max_length=255)
    committer_email = models.EmailField(max_length=255)
    message = models.TextField()

    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['hash', 'repo_name', 'repo_user']
        ordering = ['-created_on']

    def __unicode__(self):
        return u'{0}/{1}@{2}'.format(self.repo_user, self.repo_name, self.hash)

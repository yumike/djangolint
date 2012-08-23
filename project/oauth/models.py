from django.db import models
from github import Github


class AnonymousUser(object):

    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True


class User(models.Model):

    github_id = models.IntegerField(unique=True)
    github_access_token = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    def __unicode__(self):
        return self.full_name or self.username

    @property
    def github(self):
        return Github(self.github_access_token)

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

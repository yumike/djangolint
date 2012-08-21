from django.db import models
from github import Github


class User(models.Model):

    identificator = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    access_token = models.CharField(max_length=255)

    def __unicode__(self):
        return self.username

    def github(self):
        return Github(self.access_token)

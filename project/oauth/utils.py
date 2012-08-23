import hashlib
import urllib

from django.conf import settings
from github import Github
from requests_oauth2 import OAuth2

from .models import User


def get_oauth_handler():
    GITHUB = settings.GITHUB
    return OAuth2(
        GITHUB['CLIENT_ID'], GITHUB['CLIENT_SECRET'], GITHUB['AUTH_URL'],
        '', GITHUB['AUTHORIZE_URL'], GITHUB['TOKEN_URL']
    )


def get_user(access_token):
    api = Github(access_token)
    github_user = api.get_user()
    user, created = User.objects.get_or_create(
        github_id=github_user.id, defaults={
            'username': github_user.login,
            'full_name': github_user.name,
            'email': github_user.email,
            'github_access_token': access_token,
        }
    )
    if not created:
        #  Catch situation when user has changed his login
        user.username = github_user.login
        #  Or access token has been changed.
        user.github_access_token = access_token
        user.save()
    return user


def get_gravatar_url(email, size, default='identicon'):
    gravatar_url = 'http://www.gravatar.com/avatar/'
    hash = hashlib.md5(email.lower()).hexdigest()
    params = urllib.urlencode({'s': str(size), 'd': default})
    return gravatar_url + hash + '?' + params

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
        identificator=github_user.id, defaults={
            'username': github_user.login,
            'full_name': github_user.name,
            'email': github_user.email,
            'access_token': access_token,
        }
    )
    if not created:
        #  Catch situation when user has changed his login
        user.username = github_user.login
        #  Or access token has been changed.
        user.access_token = access_token
        user.save()
    return user

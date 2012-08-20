from django.conf import settings
from requests_oauth2 import OAuth2




def get_oauth_handler():
    GITHUB = settings.GITHUB
    return OAuth2(
        GITHUB['CLIENT_ID'], GITHUB['CLIENT_SECRET'],
        GITHUB['AUTH_URL'], GITHUB['CALLBACK_URL'],
    )

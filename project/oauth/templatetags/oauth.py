from django.conf import settings
from django.template import Library

from ..utils import get_oauth_handler


register = Library()


@register.simple_tag
def github_auth_url():
    oauth_handler = get_oauth_handler()
    return oauth_handler.authorize_url(settings.GITHUB['SCOPES'])

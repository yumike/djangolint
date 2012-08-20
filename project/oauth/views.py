from django.http import Http404
from django.shortcuts import redirect

from .utils import get_oauth_handler, get_user


def callback(request):
    oauth2_handler = get_oauth_handler()
    code = request.GET.get('code')
    if not code:
        raise Http404
    response = oauth2_handler.get_token(code)
    print response
    if not response or not response.get('access_token'):
        #  TODO: Show message to user, that something went wrong?
        return redirect('lint_create')
    access_token = response['access_token'][0]
    user = get_user(access_token)
    request.session['user_id'] = user.pk
    return redirect('lint_create')

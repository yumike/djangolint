from django.http import Http404
from django.shortcuts import redirect

from .utils import get_oauth_handler, get_user


def callback(request):
    oauth2_handler = get_oauth_handler()
    code = request.GET.get('code')
    if code is None:
        raise Http404
    response = oauth2_handler.get_token(code)
    if not response or response.get('access_token') is None:
        #  TODO: Show message to user, that something went wrong?
        return redirect('lint_create')
    access_token = response['access_token'][0]
    user = get_user(access_token)
    request.session['user_id'] = user.pk
    return redirect('lint_create')


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('lint_create')

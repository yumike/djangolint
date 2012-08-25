from django.utils.functional import SimpleLazyObject
from .models import User, AnonymousUser


def get_user(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return AnonymousUser()
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class UserMiddleware(object):

    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))

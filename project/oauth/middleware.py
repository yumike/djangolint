from django.utils.functional import SimpleLazyObject
from .models import User


class UserMiddleware(object):

    def process_request(self, request):
        def get_user():
            user_id = request.session.get('user_id')
            if not user_id:
                return AnonymousUser()
            try:
                return User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return AnonymousUser()
        request.user = SimpleLazyObject(get_user)

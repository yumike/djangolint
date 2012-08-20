from .models import User


def user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return {'user': None}
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return {'user': None}
    return {'user': user}

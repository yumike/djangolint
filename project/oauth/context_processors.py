from .models import User


def user(request):
    return {'user': request.user}

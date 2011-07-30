import django.views.generic.simple
from django.views.generic import list_detail
from django.views.generic.list_detail import object_detail, object_list


def index(request):
    return django.views.generic.simple.direct_to_template(
        request,
        template_name='messages/index.html')


def redirect(request):
    view = django.views.generic.simple.redirect_to
    return view(request, url='/messages/list/')


def message_list(request):
    queryset = Message.objects.filter(site=request.site)
    return list_detail.object_list(request, queryset=queryset)


def message_detail(request, object_id):
    queryset = Message.objects.filter(site=request.site)
    return object_detail(request, queryset=queryset, object_id=object_id)


def create_message(request):
    from django.views.generic.create_update import create_object
    return create_object(request)


def fake_create_message(request):
    create_object = lambda x: x
    return create_object(request)

import django.views.generic.simple
from django.shortcuts import render_to_response
from django.template import RequestContext
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


def random_message(request):
    message = Message.objects.order_by('?')[0]
    return render_to_response('messages/random.html', {'message': message},
                              context_instance=RequestContext(request))


@decorator('something')
def another_random_message(request):
    message = Message.objects.order_by('?')[0]
    return render_to_response('messages/random.html', {'message': message},
                              context_instance=RequestContext(request))


def random_message_without_request_context(request):
    message = Message.objects.order_by('?')[0]
    return render_to_response('messages/random.html', {'message': message})


def get_form_with_security_hash(request):
    from django.contrib.formtools.utils import security_hash
    form = MessageForm()
    hash = security_hash(request, form)
    return render_to_response('messages/form.html', {'form': form, 'hash': hash})


def request_context(request):
    request_context = RequestContext(request)

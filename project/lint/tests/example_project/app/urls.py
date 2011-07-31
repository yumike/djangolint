from django.conf.urls.patterns import patterns, url
from django.views.generic.simple import redirect_to


urlpatterns = patterns('',
    url(r'^redirect$', redirect_to, {'url': '/'}),
    url(r'^list$', 'messages.views.message_list'),
)

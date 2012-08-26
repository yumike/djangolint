from django.conf.urls.defaults import url, patterns

from .views import handler


urlpatterns = patterns('',
    url(r'^$', handler, name='webhooks_hook_handler'),
)

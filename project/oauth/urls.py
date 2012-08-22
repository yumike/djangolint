from django.conf.urls.defaults import url, patterns
from .views import callback, logout


urlpatterns = patterns('',
    url(r'^callback/$', callback, name='oauth_callback'),
    url(r'^logout/$', logout, name='oauth_logout'),
)

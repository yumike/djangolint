from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('oauth.views',
    url(r'^callback/$', 'callback', name='oauth_callback'),
    url(r'^logout/$', 'logout', name='oauth_logout'),
)

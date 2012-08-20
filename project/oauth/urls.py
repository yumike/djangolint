from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('oauth.views',
    url(r'^callback/$', 'callback', name='oauth_callback'),
)

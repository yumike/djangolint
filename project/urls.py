from django.conf import settings
from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    url(r'^', include('lint.urls')),
)

if settings.DEBUG:
    from django.views.generic import TemplateView
    urlpatterns += patterns(
        '',
        url(r'^404$', TemplateView.as_view(template_name='404.html')),
        url(r'^500$', TemplateView.as_view(template_name='500.html')),
    )

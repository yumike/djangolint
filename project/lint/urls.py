from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('lint.views',
    url(r'^$', 'index', name='lint_create'),
    url(r'^create$', 'create', name='lint_report_create'),
    url(r'^get_status$', 'get_status', name='lint_report_get_status'),
    url(r'^results/(?P<hash>[a-f0-9]{40})$', 'results', name='lint_results'),
)
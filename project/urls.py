from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'lint.views.index',
        name='lint_create'),
    url(r'^create$', 'lint.views.create',
        name='lint_report_create'),
    url(r'^get_status$', 'lint.views.get_status',
        name='lint_report_get_status'),
    url(r'^results/(?P<hash>[a-f0-9]{40})$', 'lint.views.results',
        name='lint_results'),
)

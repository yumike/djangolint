from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
    url(r'^$', 
        TemplateView.as_view(template_name='lint/form.html'),
        name='lint_create'),
    url(r'^create$', 'lint.views.create',
        name='lint_report_create'),
    url(r'^get_status$', 'lint.views.get_status',
        name='lint_report_get_status'),
    url(r'^results$',
        TemplateView.as_view(template_name='lint/results.html'),
        name='lint_results'),
)

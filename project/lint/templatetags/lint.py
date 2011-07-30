from django.template import Library

from ..forms import ReportForm


register = Library()


@register.inclusion_tag('lint/tags/report_create_form.html')
def report_create_form():
    return {'form': ReportForm()}

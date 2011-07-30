from django.template import Library
from django.utils import simplejson as json

from ..forms import ReportForm


register = Library()


@register.inclusion_tag('lint/tags/report_create_form.html')
def report_create_form():
    return {'form': ReportForm()}


@register.inclusion_tag('lint/tags/results_fix.html')
def results_fix(data):
    lines = json.loads(data, )
    result = []
    for line_info in lines:
        result.append({
            'number': line_info[0],
            'is_significant': line_info[1],
            'text': line_info[2],
        })
    return {'result': result}


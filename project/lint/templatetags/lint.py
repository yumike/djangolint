from django.template import Library
from django.utils import simplejson as json

from ..forms import ReportForm
from ..models import Report


register = Library()


@register.inclusion_tag('lint/tags/report_create_form.html', takes_context=True)
def report_create_form(context):
    report_pk = context.get('report_pk')
    initial_data = {}
    if report_pk is not None:
        try:
            report = Report.objects.get(pk=report_pk)
        except Report.DoesNotExist:
            report = None
        else:
            initial_data['url'] = report.url
    return {'form': ReportForm(initial=initial_data)}


@register.inclusion_tag('lint/tags/results_fix.html')
def results_fix(fix):
    source_result, solution_result = [], []
    for line_info in json.loads(fix.source):
        source_result.append({
            'number': line_info[0],
            'is_significant': line_info[1],
            'text': line_info[2],
        })
    for line_info in json.loads(fix.solution):
        solution_result.append({
            'number': line_info[0],
            'is_significant': line_info[1],
            'text': line_info[2],
        })
    return {'source_result': source_result, 'fix': fix,
            'solution_result': solution_result}

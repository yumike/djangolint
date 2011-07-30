from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import simplejson as json
from django.views.decorators.http import require_POST

from .forms import ReportForm
from .models import Report, STAGES
from .tasks import process_report


@require_POST
def create(request):
    form = ReportForm(data=request.POST or None)
    if form.is_valid():
        report = form.save()
        request.session['report_pk'] = report.pk
        process_report.delay(report)
        result = {'status': 'ok'}
    else:
        result = {'status': 'error'}
    return HttpResponse(json.dumps(result), mimetype='application/json')


def get_status(request):
    pk = request.session.get('report_pk', None)
    if pk is not None:
        result = ['waiting', 'waiting', 'waiting', 'waiting']
        report = get_object_or_404(Report, pk=pk)
        stage = report.stage
        stage_index = STAGES.index(stage)
        for status in range(stage_index):
            result[status] = 'done'
        if stage != 'done':
            result[stage_index] = 'working'
        if report.error:
            result[stage_index] = 'error'
        data = {'queue': result[0], 'cloning': result[1],
                'parsing': result[2], 'analyzing': result[3]}
    return HttpResponse(json.dumps(data), mimetype='application/json')

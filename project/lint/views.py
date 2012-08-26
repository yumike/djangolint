from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import simplejson as json
from django.views.decorators.http import require_POST

from .forms import ReportForm
from .models import Report, STAGES
from .tasks import process_report


def index(request):
    report = None
    report_pk = request.session.get('report_pk')
    if report_pk is not None:
        try:
            report = Report.objects.get(pk=report_pk)
        except Report.DoesNotExist:
            pass
    return render(request, 'lint/form.html', {'report': report})


@require_POST
def create(request):
    form = ReportForm(data=request.POST)
    report_pk = request.session.get('report_pk')
    try:
        report = Report.objects.get(pk=report_pk)
    except Report.DoesNotExist:
        report = None

    if not (report is None or report.stage == 'done' or report.error):
        data = {'status': 'error', 'error': 'You are already in the queue'}
    elif form.is_valid():
        report = form.save()
        request.session['report_pk'] = report.pk
        process_report.delay(report.pk)
        data = {'status': 'ok', 'url': report.get_absolute_url()}
    else:
        data = {'status': 'error', 'error': 'Invalid URL'}
    return HttpResponse(json.dumps(data), mimetype='application/json')


def get_status(request):
    pk = request.session.get('report_pk')
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
    return HttpResponse()


def results(request, hash):
    qs = Report.objects.filter(stage='done')
    qs = qs.exclude(error='')
    report = get_object_or_404(qs, hash=hash)
    return render(request, 'lint/results.html', {'report': report})

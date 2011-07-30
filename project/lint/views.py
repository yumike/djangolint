from django.http import HttpResponse
from django.shortcuts import render
from django.utils import simplejson as json
from django.views.decorators.http import require_POST

from .forms import ReportForm
from .tasks import process_report


@require_POST
def create(request):
    form = ReportForm(data=request.POST or None)
    if form.is_valid():
        report = form.save()
        request.session['report_hash'] = report.hash
        process_report.delay(report)
        result = {'status': 'ok'}
    else:
        result = {'status': 'error'}
    return HttpResponse(json.dumps(result), mimetype='application/json')

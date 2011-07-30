def report_pk(request):
    report_pk = request.session.get('report_pk')
    return {'report_pk': report_pk}

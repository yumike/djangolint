from celery.task import task
from django.conf import settings
from django.utils import simplejson as json
from webhooks.models import Commit
from .analyzers.loader import get_analyzers
from .ghclone import clone
from .models import Fix, Report
from .parsers import Parser


def parse(path):
    return Parser(path).parse()


def save_result(report, result):
    source = json.dumps(result.source)
    solution = json.dumps(result.solution)
    path = '/'.join(result.path.split('/')[1:]) # Remove archive dir name from result path
    Fix.objects.create(
        report=report, line=result.line, description=result.description,
        path=path, source=source, solution=solution
    )


def exception_handle(func):
    def decorator(report):
        try:
            func(report)
        except Exception, e:
            report.error = '%s: %s' % (e.__class__.__name__, unicode(e))
            report.save()
    decorator.__name__ = func.__name__
    return decorator


@task()
@exception_handle
def process_report(report_pk=None, commit_pk=None):
    if commit_pk is None and report_pk is None:
        return
    if commit_pk is not None:
        commit = Commit.objects.get(pk=commit_pk)
        if commit.report is None:
            commit.report = Report.objects.create(github_url=commit.repo_url)
            commit.save()
        report = commit.report
        head = commit.hash
    else:
        report = Report.objects.get(pk=report_pk)
        head = None

    report.stage = 'cloning'
    report.save()

    with clone(report.github_url, head) as path:
        report.stage = 'parsing'
        report.save()
        parsed_code = parse(path)

        report.stage = 'analyzing'
        report.save()
        for analyzer in get_analyzers():
            for result in analyzer(parsed_code, path).analyze():
                save_result(report, result)
        report.stage = 'done'
        report.save()

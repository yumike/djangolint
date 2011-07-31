import os
import time
from subprocess import Popen, PIPE

from celery.task import task
from django.conf import settings
from django.utils import simplejson as json

from .analyzers.loader import get_analyzers
from .models import Fix
from .parsers import Parser


class CloningError(Exception):
    pass


def clone(url, clone_path):
    error = Popen(['git', 'clone', '--depth=1', url, clone_path],
                  stdout=PIPE, stderr=PIPE).wait()
    if error:
        raise CloningError('Cloning %s repository failed' % url) 


def parse(path):
    return Parser(path).parse()


def analyze(code, path):
    results = [] 
    for analyzer in get_analyzers():
        results.extend(analyzer(code, path).analyze())
    return results


def save_results(report, results):
    for result in results:
        source = json.dumps(result.source)
        solution = json.dumps(result.solution)
        Fix.objects.create(
            report=report, line=result.line, description=result.description,
            path=result.path, source=source, solution=solution
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
def process_report(report):
    report.stage = 'cloning'
    report.save()
    path = report.get_repo_path()
    try:
        clone(report.url, path)
    except CloningError, e:
        report.error = e.message
        report.save()
        return

    report.stage = 'parsing'
    report.save()
    parsed_code = parse(path)

    report.stage = 'analyzing'
    report.save()
    save_results(report, analyze(parsed_code, path))
    report.stage = 'done'
    report.save()

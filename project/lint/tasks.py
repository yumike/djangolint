import os
import time
from subprocess import Popen, PIPE

from celery.task import task
from django.conf import settings
from django.utils import simplejson as json

from .analyzers import registry
from .models import Fix
from .parsers import Parser
from .settings import CONFIG


class CloningError(Exception):
    pass


def clone(url, hash):
    clone_path = os.path.join(CONFIG['CLONES_ROOT'], hash)
    error = Popen(['git', 'clone', url, clone_path], stdout=PIPE, stderr=PIPE).wait()
    if error:
        raise CloningError('Cloning %s repository failed' % url) 
    return clone_path


def parse(path):
    return Parser(path).parse()


def analyze(code, path):
    results = [] 
    for analyzer in registry:
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


@task()
def process_report(report):
    report.stage = 'cloning'
    report.save()
    try:
        path = clone(report.url, report.hash)
    except CloningError, e:
        report.error = e.message
        report.save()
        return

    report.stage = 'parsing'
    report.save()
    parsed_code = parse(path)

    report.stage = 'testing'
    report.save()
    save_results(report, analyze(parsed_code, path))
    report.stage = 'done'
    report.save()

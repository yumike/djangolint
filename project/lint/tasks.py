import os
import subprocess
import time

from celery.task import task
from django.conf import settings

from .settings import CONFIG


class CloningError(Exception):
    pass


def clone(url, hash):
    clone_path = os.path.join(CONFIG['CLONES_ROOT'], hash)
    error = subprocess.call(['git', 'clone', url, clone_path])
    if error:
        raise CloningError('Cloning %s repository failed' % url) 
    return clone_path


def parse(report, path):
    report.stage = 'parsing'
    report.save()
    time.sleep(5)
    result = 'ast'
    return result


def analyze(report, ast_tree):
    report.stage = 'testing'
    report.save()
    time.sleep(5)
    result = 'fixes'
    return result


@task(ignore_result=True)
def process_report(report):
    report.stage = 'cloning'
    report.save()
    try:
        path = clone(report.url, report.hash)
    except CloningError, e:
        report.error = e.text
        report.save()
        return
    ast_trees = parse(report, path)
    fixes = analyze(report, ast_trees)
    report.stage = 'finished'
    report.save()

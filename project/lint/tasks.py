import os
from subprocess import Popen, PIPE, call
import time

from celery.task import task
from django.conf import settings

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


def analyze(ast_tree):
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
        report.error = e.message
        report.save()
        return

    report.stage = 'parsing'
    report.save()
    ast_trees = parse(path)

    report.stage = 'testing'
    report.save()
    fixes = analyze(ast_trees)
    report.stage = 'done'
    report.save()

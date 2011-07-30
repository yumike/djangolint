import time
from celery.task import task


def clone(report):
    report.stage = 'cloning'
    report.save()
    result = 'filepath'
    time.sleep(5)
    return result


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
    path = clone(report)
    ast_trees = parse(report, path)
    fixes = analyze(report, ast_trees)
    report.stage = 'finished'
    report.save()

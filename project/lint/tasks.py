import os
import time
import requests
from subprocess import Popen, PIPE

from celery.task import task
from django.conf import settings
from django.utils import simplejson as json

from .analyzers.loader import get_analyzers
from .models import Fix
from .parsers import Parser
from .settings import CONFIG


class DownloadError(Exception):
    pass


def download(url, repo_path):
    user, repo = url.split('/')
    """ Get info about repo, we need python containing repos only"""
    r = requests.get('https://api.github.com/repos/%s/languages' % url)
    if r.status_code != 200:
        raise DownloadError('Not found')
    data = json.loads(r.content)
    if not 'Python' in data.keys():
        raise DownloadError("Repo language hasn't Python code")

    """ Get branch to download """
    r = requests.get('https://api.github.com/repos/%s' % url)
    data = json.loads(r.content)
    branch = data['master_branch'] or 'master'
    tarball = 'https://github.com/%s/tarball/%s' % (url, branch)

    """ Check size of branch """
    r = requests.head(tarball)
    if r.status_code != 200:
        raise DownloadError("Can't get information about tarball")
    size = r.headers['content-length']
    if int(size) > CONFIG['MAX_TARBALL_SIZE']:
        raise DownloadError("Tarball is too large: %s bytes" % size)

    """ Download and extract tarball """
    os.makedirs(repo_path)
    filepath = os.path.join(repo_path, 'archive.tar.gz')
    with open(filepath, 'wb') as f:
        f.write(requests.get(tarball).content)
    Popen(['tar', 'xf', filepath, '-C', repo_path]).wait()
    os.unlink(filepath)


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
def process_report(report):
    report.stage = 'cloning'
    report.save()
    path = report.get_repo_path()
    download(report.github_url, path)

    report.stage = 'parsing'
    report.save()
    parsed_code = parse(path)

    report.stage = 'analyzing'
    report.save()
    save_results(report, analyze(parsed_code, path))
    report.stage = 'done'
    report.save()

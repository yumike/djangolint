import os
import requests
from subprocess import Popen

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
    # Get info about repo, we need python containing repos only
    r = requests.get('https://api.github.com/repos/%s/languages' % url,
                     timeout=CONFIG['GITHUB_TIMEOUT'])
    if not r.ok or r.status_code != 200:
        raise DownloadError('Not found')
    data = json.loads(r.content)
    if not 'Python' in data.keys():
        raise DownloadError("Repo language hasn't Python code")

    # Get branch to download
    r = requests.get('https://api.github.com/repos/%s' % url,
                     timeout=CONFIG['GITHUB_TIMEOUT'])
    if not r.ok or r.status_code != 200:
        raise DownloadError('Cannot fetch information about repo')
    data = json.loads(r.content)
    branch = data['master_branch'] or 'master'
    tarball = 'https://github.com/%s/tarball/%s' % (url, branch)

    # Donwload tarball with curl
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
    filepath = os.path.join(repo_path, 'archive.tar.gz')
    curl_string = 'curl %s --connect-timeout %d --max-filesize %d -L -s -o %s' % (
        tarball, CONFIG['GITHUB_TIMEOUT'], CONFIG['MAX_TARBALL_SIZE'], filepath
    )
    if Popen(curl_string.split()).wait():
        raise DownloadError("Can't download tarball")
    if Popen(['tar', 'xf', filepath, '-C', repo_path]).wait():
        raise DownloadError("Can't extract tarball")
    os.unlink(filepath)


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
    for analyzer in get_analyzers():
        for result in analyzer(parsed_code, path).analyze():
            save_result(report, result)
    report.stage = 'done'
    report.save()

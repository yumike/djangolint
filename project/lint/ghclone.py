import os
import shutil
import requests
from contextlib import contextmanager
from subprocess import Popen
from django.utils import simplejson as json
from .settings import CONFIG


class CloneError(Exception):
    pass


@contextmanager
def clone(url, repo_path):
    _check_language(url)
    tarball_url = _get_tarball_url(url)
    tarball_path = _download_tarball(tarball_url, repo_path)
    _extract_tarball(tarball_path, repo_path)
    _remove_tarball(tarball_path)
    yield repo_path
    _remove_clone(repo_path)


def _check_language(url):
    r = requests.get('https://api.github.com/repos/%s/languages' % url,
                     timeout=CONFIG['GITHUB_TIMEOUT'])
    if not r.ok or r.status_code != 200:
        raise CloneError('Not found')
    data = json.loads(r.content)
    if not 'Python' in data.keys():
        raise CloneError("Repo language hasn't Python code")


def _get_tarball_url(url):
    r = requests.get('https://api.github.com/repos/%s' % url,
                     timeout=CONFIG['GITHUB_TIMEOUT'])
    if not r.ok or r.status_code != 200:
        raise CloneError('Cannot fetch information about repo')
    data = json.loads(r.content)
    branch = data['master_branch'] or 'master'
    return 'https://github.com/%s/tarball/%s' % (url, branch)


def _download_tarball(tarball_url, repo_path):
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
    tarball_path = os.path.join(repo_path, 'archive.tar.gz')
    curl_string = 'curl %s --connect-timeout %d --max-filesize %d -L -s -o %s' % (
        tarball_url, CONFIG['GITHUB_TIMEOUT'], CONFIG['MAX_TARBALL_SIZE'], tarball_path
    )
    if Popen(curl_string.split()).wait():
        raise CloneError("Can't download tarball")
    return tarball_path


def _extract_tarball(tarball_path, repo_path):
    if Popen(['tar', 'xf', tarball_path, '-C', repo_path]).wait():
        raise CloneError("Can't extract tarball")


def _remove_tarball(tarball_path):
    os.unlink(tarball_path)


def _remove_clone(repo_path):
    try:
        shutil.rmtree(repo_path)
    except OSError:
        pass

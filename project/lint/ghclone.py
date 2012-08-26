import errno
import os
import shutil
import tempfile
from contextlib import contextmanager
from subprocess import Popen
from django.utils import simplejson as json
from github import Github, GithubException
from .settings import CONFIG


github = Github(timeout=CONFIG['GITHUB_TIMEOUT'])


class CloneError(Exception):
    pass


@contextmanager
def tempdir(root=None):
    if root is not None:
        try:
            os.makedirs(root)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    path = tempfile.mkdtemp(dir=root)
    try:
        yield path
    finally:
        shutil.rmtree(path)


@contextmanager
def clone(url, hash=None):
    with tempdir(root=CONFIG['CLONES_ROOT']) as path:
        tarball_path = _download_tarball(url, path, hash)
        repo_path = _extract_tarball(tarball_path)
        yield repo_path


def _check_language(repo):
    if not 'Python' in repo.get_languages():
        raise CloneError("Repo language hasn't Python code")


def _get_tarball_url(repo, hash):
    return 'https://github.com/%s/%s/tarball/%s' % (
        repo.owner.login, repo.name, hash or repo.master_branch
    )


def _download_tarball(url, path, hash):
    repo_owner, repo_name = url.split('/')
    try:
        repo = github.get_user(repo_owner).get_repo(repo_name)
    except GithubException:
        raise CloneError('Not found')
    _check_language(repo)
    tarball_url = _get_tarball_url(repo, hash)
    tarball_path = os.path.join(path, 'archive.tar.gz')
    curl_string = 'curl %s --connect-timeout %d --max-filesize %d -L -s -o %s' % (
        tarball_url, CONFIG['GITHUB_TIMEOUT'], CONFIG['MAX_TARBALL_SIZE'], tarball_path
    )
    if Popen(curl_string.split()).wait():
        raise CloneError("Can't download tarball")
    return tarball_path


def _extract_tarball(tarball_path):
    repo_path = os.path.join(os.path.dirname(tarball_path), 'repo')
    os.makedirs(repo_path)
    if Popen(['tar', 'xf', tarball_path, '-C', repo_path]).wait():
        raise CloneError("Can't extract tarball")
    return repo_path

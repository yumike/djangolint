import os
import requests
from subprocess import Popen
from django.utils import simplejson as json
from .settings import CONFIG


class CloneError(Exception):
    pass


def clone(url, repo_path):
    user, repo = url.split('/')
    # Get info about repo, we need python containing repos only
    r = requests.get('https://api.github.com/repos/%s/languages' % url,
                     timeout=CONFIG['GITHUB_TIMEOUT'])
    if not r.ok or r.status_code != 200:
        raise CloneError('Not found')
    data = json.loads(r.content)
    if not 'Python' in data.keys():
        raise CloneError("Repo language hasn't Python code")

    # Get branch to download
    r = requests.get('https://api.github.com/repos/%s' % url,
                     timeout=CONFIG['GITHUB_TIMEOUT'])
    if not r.ok or r.status_code != 200:
        raise CloneError('Cannot fetch information about repo')
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
        raise CloneError("Can't download tarball")
    if Popen(['tar', 'xf', filepath, '-C', repo_path]).wait():
        raise CloneError("Can't extract tarball")
    os.unlink(filepath)

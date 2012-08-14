import json
import os

from datetime import datetime

from fabric.api import *
from fabric.contrib.files import append, exists, upload_template


@task
def vagrant():
    env.user = 'project'
    env.hosts = ['127.0.0.1:2222']
    env.project_env = 'production'


@task
def linode():
    env.user = 'project'
    env.hosts = ['djangolint.com']
    env.project_env = 'production'


@task
def bootstrap():
    with settings(user='root'):
        run('apt-get -q -y update')
        run('apt-get -q -y upgrade')
        run('apt-get -q -y install wget ssl-cert ruby ruby-dev '
            'libopenssl-ruby rdoc ri irb build-essential')
        with cd('/tmp'):
            run('wget -q http://production.cf.rubygems.org/rubygems/rubygems-1.7.2.tgz')
            run('tar xf rubygems-1.7.2.tgz')
            with cd('rubygems-1.7.2'):
                run('ruby setup.rb --no-format-executable')
            run('rm -rf rubygems-1.7.2*')
        run('gem install chef --no-ri --no-rdoc')


@task
def provision():
    project_root = os.path.dirname(env.real_fabfile)
    chef_root = os.path.join(project_root, 'chef')
    chef_name = 'chef-{0}'.format(datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S'))
    chef_archive = '{0}.tar.gz'.format(chef_name)

    local('cp -r {0} /tmp/{1}'.format(chef_root, chef_name))

    with open('node.json') as f:
        data = json.load(f)
    project = data.setdefault('project', {})
    project['environment'] = env.project_env
    with open('/tmp/{0}/node.json'.format(chef_name), 'w') as f:
        json.dump(data, f)

    solo_rb = ('file_cache_path "/tmp/chef-solo"',
               'cookbook_path "/tmp/{0}/cookbooks"'.format(chef_name))
    with lcd('/tmp'):
        for line in solo_rb:
            local("echo '{0}' >> {1}/solo.rb".format(line, chef_name))
        local('tar czf {0} {1}'.format(chef_archive, chef_name))

    with settings(user='root'):
        put('/tmp/{0}'.format(chef_archive), '/tmp/{0}'.format(chef_archive))
        local('rm -rf /tmp/{0}*'.format(chef_name))
        with cd('/tmp'):
            run('tar xf {0}'.format(chef_archive))
        with cd('/tmp/{0}'.format(chef_name)):
            with settings(warn_only=True):
                run('chef-solo -c solo.rb -j node.json')
        run('rm -rf /tmp/{0}*'.format(chef_name))
    upload_public_key('project', 'root')
    prepare_env()


@task
def prepare_env():
    if not exists('.env'):
        run('wget https://raw.github.com/pypa/virtualenv/develop/virtualenv.py')
        run('python virtualenv.py --distribute --no-site-packages ~/.env')
        run("echo 'source ~/.env/bin/activate' >> .profile")
    if not exists('.git'):
        run('git init .git --bare')
        run('git clone .git project')
    local('git push ssh://{user}@{host}:{port}/~/.git master'.format(**env))
    with cd('project'):
        run('git pull ~/.git master')
        install_requirements()
        manage('syncdb --migrate --noinput')
        manage('collectstatic --noinput')
    with open('etc/supervisord.conf') as f:
        supervisor_config = f.read().format(**{'project_env': env.project_env})
        run('mkdir -p ~/etc/ && rm -f ~/etc/supervisord.conf')
        append('~/etc/supervisord.conf', supervisor_config)
    with settings(user='root', warn_only=True):
        with lcd('etc'):
            put('supervisor_upstart.conf', '/etc/init/supervisor.conf')
            run('stop supervisor')
            run('start supervisor')


@task
def deploy(update_all='yes'):
    local('git push ssh://{user}@{host}:{port}/~/.git master'.format(**env))
    with cd('project'):
        run('git pull ~/.git master')
        if update_all == 'yes':
            install_requirements()
            manage('syncdb --migrate --noinput')
            manage('collectstatic --noinput')
            upload_crontab()
    run('supervisorctl restart gunicorn')
    run('supervisorctl restart celery')


@task
def install_requirements():
    run('pip install -r requirements/{0}.txt'.format(env.project_env))


@task
def manage(command):
    run('python project/manage.py {0}'.format(command))


@task
def upload_public_key(to=None, user=None):
    with settings(user=user or env.user):
        to = to or env.user
        path = os.path.expanduser('~/.ssh/id_rsa.pub')
        if to and os.path.exists(path):
            key = ' '.join(open(path).read().strip().split(' ')[:2])
            run('mkdir -p /home/{0}/.ssh'.format(to))
            append('/home/{0}/.ssh/authorized_keys'.format(to), key, partial=True)
            run('chown {0}:{0} /home/{0}/.ssh/authorized_keys'.format(to))
            run('chmod 600 /home/{0}/.ssh/authorized_keys'.format(to))
            run('chown {0}:{0} /home/{0}/.ssh'.format(to))
            run('chmod 700 /home/{0}/.ssh'.format(to))


@task
def upload_crontab():
    project_root = os.path.dirname(env.real_fabfile)
    crontab_path = os.path.join('etc', 'crontab')
    if not os.path.exists(crontab_path):
        return
    upload_template(
        filename=crontab_path,
        destination='crontab.tmp',
        context={'environment': env.project_env},
    )
    run('crontab < crontab.tmp')
    #run('rm crontab.tmp')

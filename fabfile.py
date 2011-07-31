import json
import os

from datetime import datetime

from fabric.api import *


@task
def vagrant():
    env.user = 'project'
    env.hosts = ['127.0.0.1:2222']
    env.project_env = 'production'


@task
def bootstrap():
    with settings(user='root'):
        run('apt-get -q -y update')
        run('apt-get -q -y upgrade')
        run('apt-get -q -y install wget ssl-cert ruby ruby-dev '
            'libopenssl-ruby rdoc ri irb')
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
    create_node_json('/tmp/{0}/node.json'.format(chef_name))
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


def create_node_json(target):
    with open('node.json') as f:
        data = json.load(f)
    project = data.setdefault('project', {})
    project['environment'] = env.project_env
    with open(target, 'w') as f:
        json.dump(data, f)

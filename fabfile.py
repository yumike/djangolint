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

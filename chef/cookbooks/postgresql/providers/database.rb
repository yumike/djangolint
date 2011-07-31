require 'chef/mixin/shell_out'
include Chef::Mixin::ShellOut

action :create do
  unless exists?
    Chef::Log.info("Creating #{new_resource}")
    execute "createdb #{options} #{new_resource.name}" do
      user "postgres"
    end
  end
end

def options
  options = "--owner #{new_resource.owner}"
  options += " --encoding=#{new_resource.encoding}"
  options += " --locale=#{new_resource.locale}"
end

def exists?
  @exists ||= begin
    sql = "select count(*) from pg_database where datname='#{new_resource.name}'"
    out = shell_out("test `sudo -u postgres psql -c \"#{sql}\" -t` = '0'")
    out.exitstatus == 1
  end
end

require 'chef/mixin/shell_out'
include Chef::Mixin::ShellOut

action :create do
  unless exists?
    Chef::Log.info("Creating #{new_resource}")
    execute "createuser -dRS #{new_resource.name}" do
      user "postgres"
    end
  end
end

def exists?
  @exists ||= begin
    sql = "select count(*) from pg_roles where rolname='#{new_resource.name}'"
    out = shell_out("test `sudo -u postgres psql -c \"#{sql}\" -t` = '0'")
    out.exitstatus == 1
  end
end

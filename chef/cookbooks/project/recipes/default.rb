group "project"

user "project" do
  gid "project"
  home "/home/project"
  shell "/bin/bash"
end

directory "/home/project" do
  owner "project"
  group "project"
  mode 0700
end

directory "/home/project/.ssh" do
  owner "project"
  group "project"
  mode 0700
end

execute "echo 'export PROJECT_ENV=#{node[:project][:environment]}' >> /home/project/.profile" do
  user "project"
  group "project"
  not_if "cat /home/project/.profile | grep 'export PROJECT_ENV=#{node[:project][:environment]}'"
end

directory "/usr/share/nginx/www/project" do
  owner "project"
  group "project"
  mode 0755
end

postgresql_user "project"

postgresql_database "project" do
  owner "project"
end

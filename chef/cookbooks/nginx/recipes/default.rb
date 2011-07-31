package "nginx"

cookbook_file "/etc/nginx/mime.types" do
  source "mime.types"
  owner "root"
  group "root"
  mode 0644
  notifies :reload, "service[nginx]"
end

cookbook_file "/etc/nginx/nginx.conf" do
  source "nginx.conf"
  owner "root"
  group "root"
  mode 0644
  notifies :reload, "service[nginx]"
end

cookbook_file "/etc/nginx/sites-available/default" do
  source "default.conf"
  owner "root"
  group "root"
  mode 0644
  notifies :reload, "service[nginx]"
end

service "nginx" do
  action [:enable, :start]
  supports :status => true, :restart => true, :reload => true
end

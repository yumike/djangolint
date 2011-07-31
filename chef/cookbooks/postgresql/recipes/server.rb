include_recipe "postgresql::client"

package "postgresql" do
  action :install
end

service "postgresql" do
  action [:enable, :start]
  supports :status => true, :restart => true, :reload => true
end

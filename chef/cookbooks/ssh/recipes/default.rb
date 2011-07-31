template "/etc/ssh/sshd_config" do
  source "sshd_config.erb"
  group "root"
  owner "root"
  mode 0644
end

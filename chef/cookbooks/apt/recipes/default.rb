e = execute "apt-get update" do
  action :nothing
end

e.run_action(:run)

Vagrant::Config.run do |config|
  config.vm.box = "maverick"
  config.vm.forward_port "http", 80, 8080
  config.vm.forward_port "ssh", 22, 2222
end

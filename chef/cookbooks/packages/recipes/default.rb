[
  "#{node[:platform]}-#{node[:platform_version]}",
  node[:platform],
  "default"
].compact.each do |scope|
  if node[:packages][scope]
    node[:packages][scope].each do |name|
      package name
    end
    break
  end
end

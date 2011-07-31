include_recipe "curl"

package "python"
package "python-dev"

execute "curl http://python-distribute.org/distribute_setup.py | python" do
  not_if "which easy_install"
end

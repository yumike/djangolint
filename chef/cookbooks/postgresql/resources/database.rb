actions :create

attribute :name, :kind_of => String, :name_attribute => true
attribute :owner, :regex => Chef::Config[:user_valid_regex], :required => true
attribute :encoding, :kind_of => String, :default => "UTF8"
attribute :locale, :kind_of => String

def initialize(*args)
  super
  @action = :create
end

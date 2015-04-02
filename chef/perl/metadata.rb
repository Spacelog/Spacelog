name              'perl'
maintainer        'Opscode, Inc.'
maintainer_email  'cookbooks@opscode.com'
license           'Apache 2.0'
description       'Installs perl and provides a define for maintaining CPAN modules'
long_description  IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version           '1.2.4'

recipe 'perl', 'Installs perl and adds a provider to install cpan modules'

%w{ ubuntu debian mint redhat centos amazon scientific oracle fedora arch}.each do |os|
  supports os
end

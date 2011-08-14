execute "apt-get update"

%w{python python-setuptools python-pip redis-server python-redis
    python-virtualenv imagemagick subversion git-core python-xapian}.each { |p|
  package p
}

include_recipe "perl"

cpan_module "CSS::Prepare"

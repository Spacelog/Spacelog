execute "apt-get update"

%w{python python-setuptools python-pip redis-server python-redis
    python-virtualenv imagemagick subversion git-core python-xapian
    ruby-sass}.each { |p|
  package p
}

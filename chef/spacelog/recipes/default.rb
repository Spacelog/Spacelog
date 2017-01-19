execute "apt-get update"

%w{python python-setuptools python-pip redis-server python-redis
    python-virtualenv imagemagick optipng procps git-core python-xapian
    }.each { |p|
  package p
}

{
  "LC_ALL" => "en_US.utf-8",
  "PYTHON" => `which python`,
}.each do |variable, value|
  line = "#{variable}=#{value}"
  matcher = %r(^#{variable}=)

  edit = Chef::Util::FileEdit.new("/etc/environment")
  edit.search_file_replace_line(matcher, line)
  edit.insert_line_if_no_match(matcher, line)
  edit.write_file
end

execute "pip install -U pip"
execute "pip install -r /vagrant/requirements.txt"

#
# Cookbook Name:: perl
# Recipe:: default
#
# Copyright 2009-2013, Opscode, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

case node['platform']
when 'windows'
  include_recipe 'perl::_windows'

else
  node['perl']['packages'].each do |perl_pkg|
    package perl_pkg
  end

  cpanm = node['perl']['cpanm'].to_hash
  root_group = node['platform'] == 'mac_os_x' ? 'admin' : 'root'

  directory File.dirname(cpanm['path']) do
    recursive true
  end

  remote_file cpanm['path'] do
    source cpanm['url']
    checksum cpanm['checksum']
    owner 'root'
    group root_group
    mode 0755
  end
end

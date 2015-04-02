#
# Cookbook Name:: perl
# Definition:: cpan_module
#
# Copyright 2009, Opscode, Inc.
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

# TODO: convert this to an LWRP
define :cpan_module, :force => nil do
  execute "install-#{params[:name]}" do
    if params[:force]
      command "#{node['perl']['cpanm']['path']} --force --notest #{params[:name]}"
    else
      command "#{node['perl']['cpanm']['path']} --notest #{params[:name]}"
    end
    root_dir = node['platform'] == 'mac_os_x' ? '/var/root' : '/root'
    cwd root_dir
    # Will create working dir on /root/.cpanm (or /var/root)
    environment 'HOME' => root_dir
    path %w{ /usr/local/bin /usr/bin /bin }
    not_if "perl -m#{params[:name]} -e ''"
  end
end

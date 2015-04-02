#
# Cookbook Name:: perl
# Attributes:: default
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

case node['platform_family']
when 'rhel'
  default['perl']['packages'] = %w{ perl perl-libwww-perl perl-CPAN }

  case node['platform_version'].to_i
  when 5
    default['perl']['packages'] = %w{ perl perl-libwww-perl  }
  when 6
    default['perl']['packages'] = %w{ perl perl-libwww-perl perl-CPAN }
  end

when 'debian'
  default['perl']['packages'] = %w{ perl libperl-dev }
when 'arch'
  default['perl']['packages'] = %w{ perl perl-libwww }
when 'omnios'
  default['perl']['packages'] = %w{ perl }
when 'windows'
  default['perl']['maj_version'] = '5'
  default['perl']['min_version'] = '16'
  default['perl']['sub_version'] = '1.1'

  case node['kernel']['machine'].to_s
  when 'x86_64'
    default['perl']['bitness'] = '64bit'
  else
    default['perl']['bitness'] = '32bit'
  end

else
  default['perl']['packages'] = %w{ perl libperl-dev }
end

default['perl']['cpanm']['url'] = 'https://raw.github.com/miyagawa/cpanminus/1.6922/cpanm'
default['perl']['cpanm']['checksum'] = 'cb35d3f1ac8f59c1458e1f67308c9caa4959f3912dfeac603b8aff29c6fe643d'
default['perl']['cpanm']['path'] = '/usr/local/bin/cpanm'

default['perl']['install_dir'] = 'C:\\perl\\'

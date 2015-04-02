perl Cookbook
=============
Manages Perl installation and provides `cpan_module`, to install modules from... CPAN.


Requirements
------------
### Platforms
- Debian/Ubuntu/Mint
- RHEL/CentOS/Scientific/Oracle/Fedora
- ArchLinux
- Windows


Attributes
----------
- perl\['packages'\] - platform specific packages installed by default recipe
- perl\['cpanm'\]\['path'\] - platform specific path for `cpanm` binary to live
- perl\['cpanm'\]\['url'\] - URL to download cpanm script from
- perl\['cpanm'\]\['checksum'\] - checksum for the above remote file


Usage
-----
To install a module from CPAN:

```ruby
cpan_module 'App::Munchies'
```

Optionally, installation can forced with the 'force' parameter.

```ruby
cpan_module 'App::Munchies'
  force true
end


License & Authors
-----------------
- Author:: Joshua Timberman (<joshua@opscode.com>)

```text
Copyright:: 2009, Opscode, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

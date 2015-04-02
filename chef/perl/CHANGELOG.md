perl Cookbook CHANGELOG
=======================
This file is used to list changes made in each version of the perl cookbook.


v1.2.4 (2014-06-16)
-------------------
- [COOK-4725] Use windows_path to set the PATH


v1.2.2
------
### New Feature
- **[COOK-4013](https://tickets.opscode.com/browse/COOK-4013)** - add omnios support to perl cookbook


v1.2.0
------
### Improvement
- **[COOK-3230](https://tickets.opscode.com/browse/COOK-3230)** - Upgrade cpanm
- **[COOK-2998](https://tickets.opscode.com/browse/COOK-2998)** - Improve install speed by using `--notest`

v1.1.2
------
### Bug
- [COOK-2973]: perl cookbook has foodcritic errors

v1.1.0
------
- [COOK-1765] - Install Strawberry Perl on Windows in Perl Cookbook

v1.0.2
------
- [COOK-1300] - add support for Mac OS X

v1.0.0
------
- [COOK-1129] - move lists of perl packages to attributes by platform
- [COOK-1279] - resolve regression from COOK-1129
- [COOK-1299] - use App::cpanminus (cpanm) to install "cpan packages"

v0.10.2
------
- [COOK-1279] Re-factor recipe and fix platform_version 5 bug for redhat family platforms

v0.10.1
------
- [COOK-1129] centos/redhat needs the CPAN RPM installed

v0.10.0
------
- Current released version

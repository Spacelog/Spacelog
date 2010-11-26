# Copyright (C) 2008 Lemur Consulting Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
r"""_checkxapian.py: Check the version of xapian used.

Raises an ImportError on import if the version used is too old to be used at
all.

"""
__docformat__ = "restructuredtext en"

# The minimum version of xapian required to work at all.
min_xapian_version = (1, 0, 6)

# Dictionary of features we can't support do to them being missing from the
# available version of xapian.
missing_features = {}

import xapian

versions = xapian.major_version(), xapian.minor_version(), xapian.revision()


if versions < min_xapian_version:
    raise ImportError("""
        Xapian Python bindings installed, but need at least version %d.%d.%d - got %s
        """.strip() % tuple(list(min_xapian_version) + [xapian.version_string()]))

if not hasattr(xapian, 'TermCountMatchSpy'):
    missing_features['tags'] = 1
if not hasattr(xapian, 'CategorySelectMatchSpy'):
    missing_features['facets'] = 1

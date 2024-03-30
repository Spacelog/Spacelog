#!/usr/bin/env python
#
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
r"""schema.py: xdefinitions and implementations of field actions.

"""
__docformat__ = "restructuredtext en"

from . import errors as _errors
from .replaylog import log as _log
from . import parsedate as _parsedate

class Schema(object):
    def __init__(self):
        pass

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod (sys.modules[__name__])

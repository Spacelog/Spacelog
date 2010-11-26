#!/usr/bin/env python
#
# Copyright (C) 2007 Lemur Consulting Ltd
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
r"""marshall.py: Marshal values into strings

"""
__docformat__ = "restructuredtext en"

import math
import xapian
from replaylog import log as _log

def float_to_string(value):
    """Marshall a floating point number to a string which sorts in the
    appropriate manner.

    """
    return _log(xapian.sortable_serialise, value)

def date_to_string(date):
    """Marshall a date to a string which sorts in the appropriate manner.

    """
    return '%04d%02d%02d' % (date.year, date.month, date.day)

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
"""Xappy.

See the accompanying documentation for details.  In particular, there should be
an accompanying file "introduction.html" (or "introduction.rst") which gives
details of how to use the xappy package.

"""
__docformat__ = "restructuredtext en"

__version__ = '0.5'

from . import _checkxapian
from .datastructures import Field, UnprocessedDocument, ProcessedDocument
from .errors import *
from .fieldactions import FieldActions
from .indexerconnection import IndexerConnection
from .searchconnection import SearchConnection
from .replaylog import set_replay_path

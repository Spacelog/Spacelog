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
r"""fieldmappings.py: Mappings from field names to term prefixes, etc.

"""
__docformat__ = "restructuredtext en"

import cPickle as _cPickle

class FieldMappings(object):
    """Mappings from field names to term prefixes, slot values, etc.

    The following mappings are maintained:

    - a mapping from field name to the string prefix to insert at the start of
      terms.
    - a mapping from field name to the slot numbers to store the field contents
      in.

    """
    __slots__ = '_prefixes', '_prefixcount', '_slots', '_slotcount', 

    def __init__(self, serialised=None):
        """Create a new field mapping object, or unserialise a saved one.

        """
        if serialised is not None:
            (self._prefixes, self._prefixcount,
             self._slots, self._slotcount) = _cPickle.loads(serialised)
        else:
            self._prefixes = {}
            self._prefixcount = 0
            self._slots = {}
            self._slotcount = 0

    def _genPrefix(self):
        """Generate a previously unused prefix.

        Prefixes are uppercase letters, and start with 'X' (this is a Xapian
        convention, for compatibility with other Xapian tools: other starting
        letters are reserved for special meanings):

        >>> maps = FieldMappings()
        >>> maps._genPrefix()
        'XA'
        >>> maps._genPrefix()
        'XB'
        >>> [maps._genPrefix() for i in xrange(60)]
        ['XC', 'XD', 'XE', 'XF', 'XG', 'XH', 'XI', 'XJ', 'XK', 'XL', 'XM', 'XN', 'XO', 'XP', 'XQ', 'XR', 'XS', 'XT', 'XU', 'XV', 'XW', 'XX', 'XY', 'XZ', 'XAA', 'XBA', 'XCA', 'XDA', 'XEA', 'XFA', 'XGA', 'XHA', 'XIA', 'XJA', 'XKA', 'XLA', 'XMA', 'XNA', 'XOA', 'XPA', 'XQA', 'XRA', 'XSA', 'XTA', 'XUA', 'XVA', 'XWA', 'XXA', 'XYA', 'XZA', 'XAB', 'XBB', 'XCB', 'XDB', 'XEB', 'XFB', 'XGB', 'XHB', 'XIB', 'XJB']
        >>> maps = FieldMappings()
        >>> [maps._genPrefix() for i in xrange(27*26 + 5)][-10:]
        ['XVZ', 'XWZ', 'XXZ', 'XYZ', 'XZZ', 'XAAA', 'XBAA', 'XCAA', 'XDAA', 'XEAA']
        """
        res = []
        self._prefixcount += 1
        num = self._prefixcount
        while num != 0:
            ch = (num - 1) % 26
            res.append(chr(ch + ord('A')))
            num -= ch
            num = num // 26
        return 'X' + ''.join(res)

    def get_fieldname_from_prefix(self, prefix):
        """Get a fieldname from a prefix.

        If the prefix is not found, return None.

        """
        for key, val in self._prefixes.iteritems():
            if val == prefix:
                return key
        return None

    def get_prefix(self, fieldname):
        """Get the prefix used for a given field name.

        """
        return self._prefixes[fieldname]

    def get_slot(self, fieldname, purpose):
        """Get the slot number used for a given field name and purpose.

        """
        return self._slots[(fieldname, purpose)]

    def add_prefix(self, fieldname):
        """Allocate a prefix for the given field.

        If a prefix is already allocated for this field, this has no effect.

        """
        if fieldname in self._prefixes:
            return
        self._prefixes[fieldname] = self._genPrefix()

    def add_slot(self, fieldname, purpose, slotnum=None):
        """Allocate a slot number for the given field and purpose.

        If a slot number is already allocated for this field and purpose, this
        has no effect.

        Returns the slot number allocated for the field and purpose (whether
        newly allocated, or previously allocated).

        If `slotnum` is supplied, the number contained in it is used to
        allocate the new slot, instead of allocating a new number.  No checks
        will be made to ensure that the slot number doesn't collide with
        existing (or later allocated) numbers: the main purpose of this
        parameter is to share allocations - ie, to collide deliberately.

        """
        try:
            return self._slots[(fieldname, purpose)]
        except KeyError:
            pass

        if slotnum is None:
            self._slots[(fieldname, purpose)] = self._slotcount
            self._slotcount += 1
            return self._slotcount - 1
        else:
            self._slots[(fieldname, purpose)] = slotnum
            return slotnum

    def serialise(self):
        """Serialise the field mappings to a string.

        This can be unserialised by passing the result of this method to the
        constructor of a new FieldMappings object.

        """
        return _cPickle.dumps((self._prefixes,
                               self._prefixcount,
                               self._slots,
                               self._slotcount,
                              ), 2)

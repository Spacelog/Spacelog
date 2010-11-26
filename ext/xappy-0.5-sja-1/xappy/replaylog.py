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
r"""replaylog.py: Log all xapian calls to a file, so that they can be replayed.

"""
__docformat__ = "restructuredtext en"

import datetime
import sys
import thread
import threading
import time
import traceback
import types
import weakref
import xapian

from pprint import pprint

# The logger in use.
_replay_log = None

# True if a replay log has ever been in use since import time.
_had_replay_log = False

class NotifyingDeleteObject(object):
    """An wrapping for an object which calls a callback when its deleted.

    Note that the callback will be called from a __del__ method, so shouldn't
    raise any exceptions, and probably shouldn't make new references to the
    object supplied to it.

    """
    def __init__(self, obj, callback):
        self.obj = obj
        self.callback = callback

    def __del__(self):
        self.callback(self.obj)

class ReplayLog(object):
    """Log of xapian calls, to be replayed.

    """

    def __init__(self, logpath):
        """Create a new replay log.

        """
        # Mutex used to protect all access to _fd
        self._fd_mutex = threading.Lock()
        self._fd = file(logpath, 'wb')

        # Mutex used to protect all access to members other than _fd
        self._mutex = threading.Lock()
        self._next_call = 1

        self._next_thread = 0
        self._thread_ids = {}

        self._objs = weakref.WeakKeyDictionary()
        self._next_num = 1

        self._xapian_classes = {}
        self._xapian_functions = {}
        self._xapian_methods = {}
        for name in dir(xapian):
            item = getattr(xapian, name)
            has_members = False
            for membername in dir(item):
                member = getattr(item, membername)
                if isinstance(member, types.MethodType):
                    self._xapian_methods[member.im_func] = (name, membername)
                    has_members = True
            if has_members:
                self._xapian_classes[item] = name
            if isinstance(item, types.BuiltinFunctionType):
                self._xapian_functions[item] = name

    def _get_obj_num(self, obj, maybe_new):
        """Get the number associated with an object.

        If maybe_new is False, a value of 0 will be supplied if the object
        hasn't already been seen.  Otherwise, a new (and previously unused)
        value will be allocated to the object.

        The mutex should be held when this is called.

        """
        try:
            num = self._objs[obj]
            return num.obj
        except KeyError:
            pass

        if not maybe_new:
            return 0

        self._objs[obj] = NotifyingDeleteObject(self._next_num, self._obj_gone)
        self._next_num += 1
        return self._next_num - 1

    def _is_xap_obj(self, obj):
        """Return True iff an object is an instance of a xapian object.

        (Also returns true if the object is an instance of a subclass of a
        xapian object.)

        The mutex should be held when this is called.

        """
        # Check for xapian classes.
        classname = self._xapian_classes.get(type(obj), None)
        if classname is not None:
            return True
        # Check for subclasses of xapian classes.
        for classobj, classname in self._xapian_classes.iteritems():
            if isinstance(obj, classobj):
                return True
        # Not a xapian class or subclass.
        return False

    def _get_xap_name(self, obj, maybe_new=False):
        """Get the name of a xapian class or method.

        The mutex should be held when this is called.

        """
        # Check if it's a xapian class, or subclass.
        if isinstance(obj, types.TypeType):
            classname = self._xapian_classes.get(obj, None)
            if classname is not None:
                return classname

            for classobj, classname in self._xapian_classes.iteritems():
                if issubclass(obj, classobj):
                    return "subclassof_%s" % (classname, )

            return None

        # Check if it's a xapian function.
        if isinstance(obj, types.BuiltinFunctionType):
            funcname = self._xapian_functions.get(obj, None)
            if funcname is not None:
                return funcname

        # Check if it's a proxied object.
        if isinstance(obj, LoggedProxy):
            classname = self._xapian_classes.get(obj.__class__, None)
            if classname is not None:
                objnum = self._get_obj_num(obj, maybe_new=maybe_new)
                return "%s#%d" % (classname, objnum)

        # Check if it's a proxied method.
        if isinstance(obj, LoggedProxyMethod):
            classname, methodname = self._xapian_methods[obj.real.im_func]
            objnum = self._get_obj_num(obj.proxyobj, maybe_new=maybe_new)
            return "%s#%d.%s" % (classname, objnum, methodname)

        # Check if it's a subclass of a xapian class.  Note: this will only
        # pick up subclasses, because the original classes are filtered out
        # higher up.
        for classobj, classname in self._xapian_classes.iteritems():
            if isinstance(obj, classobj):
                objnum = self._get_obj_num(obj, maybe_new=maybe_new)
                return "subclassof_%s#%d" % (classname, objnum)

        return None

    def _log(self, msg):
        self._fd_mutex.acquire()
        try:
#            msg = '%s,%s' % (
#                datetime.datetime.fromtimestamp(time.time()).isoformat(),
#                msg,
#            )
            self._fd.write(msg)
            self._fd.flush()
        finally:
            self._fd_mutex.release()

    def _repr_arg(self, arg):
        """Return a representation of an argument.

        The mutex should be held when this is called.

        """

        xapargname = self._get_xap_name(arg)
        if xapargname is not None:
            return xapargname

        if isinstance(arg, basestring):
            if isinstance(arg, unicode):
                arg = arg.encode('utf-8')
            return 'str(%d,%s)' % (len(arg), arg)

        if isinstance(arg, long):
            try:
                arg = int(arg)
            except OverFlowError:
                pass

        if isinstance(arg, long):
            return 'long(%d)' % arg

        if isinstance(arg, int):
            return 'int(%d)' % arg

        if isinstance(arg, float):
            return 'float(%f)' % arg

        if arg is None:
            return 'None'

        if hasattr(arg, '__iter__'):
            seq = []
            for item in arg:
                seq.append(self._repr_arg(item))
            return 'list(%s)' % ','.join(seq)

        return 'UNKNOWN:' + str(arg)

    def _repr_args(self, args):
        """Return a representation of a list of arguments.

        The mutex should be held when this is called.

        """
        logargs = []
        for arg in args:
            logargs.append(self._repr_arg(arg))
        return ','.join(logargs)

    def _get_call_id(self):
        """Get an ID string for a call.

        The mutex should be held when this is called.

        """
        call_num = self._next_call
        self._next_call += 1

        thread_id = thread.get_ident()
        try:
            thread_num = self._thread_ids[thread_id]
        except KeyError:
            thread_num = self._next_thread
            self._thread_ids[thread_id] = thread_num
            self._next_thread += 1

        if thread_num is 0:
            return "%s" % call_num
        return "%dT%d" % (call_num, thread_num)

    def log_call(self, call, *args):
        """Add a log message about a call.

        Returns a number for the call, so it can be tied to a particular
        result.

        """
        self._mutex.acquire()
        try:
            logargs = self._repr_args(args)
            xapobjname = self._get_xap_name(call)
            call_id = self._get_call_id()
        finally:
            self._mutex.release()

        if xapobjname is not None:
            self._log("CALL%s:%s(%s)\n" % (call_id, xapobjname, logargs))
        else:
            self._log("CALL%s:UNKNOWN:%r(%s)\n" % (call_id, call, logargs))
        return call_id

    def log_except(self, (etype, value, tb), call_id):
        """Log an exception which has occurred.

        """
        # No access to an members, so no need to acquire mutex.
        exc = traceback.format_exception_only(etype, value)
        self._log("EXCEPT%s:%s\n" % (call_id, ''.join(exc).strip()))

    def log_retval(self, ret, call_id):
        """Log a return value.

        """
        if ret is None:
            self._log("RET%s:None\n" % call_id)
            return

        self._mutex.acquire()
        try:
            # If it's a xapian object, return a proxy for it.
            if self._is_xap_obj(ret):
                ret = LoggedProxy(ret)
                xapobjname = self._get_xap_name(ret, maybe_new=True)
            msg = "RET%s:%s\n" % (call_id, self._repr_arg(ret))
        finally:
            self._mutex.release()

        # Not a xapian object - just return it.
        self._log(msg)
        return ret

    def _obj_gone(self, num):
        """Log that an object has been deleted.

        """
        self._log('DEL:#%d\n' % num)

class LoggedProxy(object):
    """A proxy for a xapian object, which logs all calls made on the object.

    """
    def __init__(self, obj):
        self.__obj = obj

    def __getattribute__(self, name):
        obj = object.__getattribute__(self, '_LoggedProxy__obj')
        if name == '__obj':
            return obj
        real = getattr(obj, name)
        if not isinstance(real, types.MethodType):
            return real
        return LoggedProxyMethod(real, self)

    def __iter__(self):
        obj = object.__getattribute__(self, '_LoggedProxy__obj')
        return obj.__iter__()

    def __len__(self):
        obj = object.__getattribute__(self, '_LoggedProxy__obj')
        return obj.__len__()

    def __repr__(self):
        obj = object.__getattribute__(self, '_LoggedProxy__obj')
        return '<LoggedProxy of %s >' % obj.__repr__()

    def __str__(self):
        obj = object.__getattribute__(self, '_LoggedProxy__obj')
        return obj.__str__()

class LoggedProxyMethod(object):
    """A proxy for a xapian method, which logs all calls made on the method.

    """
    def __init__(self, real, proxyobj):
        """Make a proxy for the method.

        """
        self.real = real
        self.proxyobj = proxyobj

    def __call__(self, *args):
        """Call the proxied method, logging the call.

        """
        return log(self, *args)

def set_replay_path(logpath):
    """Set the path for the replay log.

    """
    global _replay_log
    global _had_replay_log
    if logpath is None:
        _replay_log = None
    else:
        _had_replay_log = True
        _replay_log = ReplayLog(logpath)

def _unproxy_call_and_args(call, args):
    """Convert a call and list of arguments to unproxied form.

    """
    if isinstance(call, LoggedProxyMethod):
        realcall = call.real
    else:
        realcall = call

    realargs = []
    for arg in args:
        if isinstance(arg, LoggedProxy):
            arg = arg.__obj
        realargs.append(arg)

    return realcall, realargs

def log(call, *args):
    """Make a call to xapian, and log it.

    """
    # If we've never had a replay log in force, no need to unproxy objects.
    global _had_replay_log
    if not _had_replay_log:
        return call(*args)

    # Get unproxied versions of the call and arguments.
    realcall, realargs = _unproxy_call_and_args(call, args)

    # If we have no replay log currently, just do the call.
    global _replay_log
    replay_log = _replay_log
    if replay_log is None:
        return realcall(*realargs)

    # We have a replay log: do a logged version of the call.
    call_id = replay_log.log_call(call, *args)
    try:
        ret = realcall(*realargs)
    except:
        replay_log.log_except(sys.exc_info(), call_id)
        raise
    return replay_log.log_retval(ret, call_id)

#set_replay_path('replay.log')

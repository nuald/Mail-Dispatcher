#    This file is part of Maildispatcher.
#
#    Maildispatcher is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Maildispatcher is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Maildispatcher.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright 2007-2008 Alex Slesarev

"""utils.py
Module with utilities functions."""

import traceback
import sys
import threading
import gtk, gobject
import os
import time

def print_exception(exception, message):
    """Print exception information to stderr.
    'exception' is the exception instance.
    'message' is the message for exception."""
    print >> sys.stderr, message, ': %s' % exception
    print >> sys.stderr, '-' * 60
    traceback.print_exc(file = sys.stderr)
    print >> sys.stderr, '-' * 60

def find(pathname):
    """Resolve pathname to a location on the Python path.
    'pathname' is the path to file."""
    if os.path.isabs(pathname):
        return pathname
    for dirname in sys.path:
        candidate = os.path.join(dirname, pathname)
        if os.path.isfile(candidate):
            return candidate
    raise OSError(_('Cannot find %(pathname)s on the Python path.') % locals())

def threaded(function):
    """Helper for threading.
    'function' is the decorated function."""
    def wrapper(*args):
        """Thread wrapper.
        'args' is the arguments of the decorated function."""
        thread = threading.Thread(target = function, args = args)
        thread.start()
    return wrapper

def idlefunction(function):
    """Helper for idle mode.
    'function' is the decorated function."""
    def in_idle(args, params):
        """Put function in GUI thread.
        'args' is the arguments of the decorated function.
        'params' is the parameters of the decorated function."""
        gtk.gdk.threads_enter()
        try:
            # Have to use magic for passing parameters
            function(*args, **params) # pylint: disable-msg=W0142
            return False
        finally:
            gtk.gdk.threads_leave()
    def wrapper(*args, **params):
        """Wrapper for idle function.
        'args' is the arguments of the decorated function.
        'params' is the parameters of the decorated function."""
        gobject.idle_add(in_idle, args, params)
    return wrapper

def setup_gettext():
    """Set up gettext environment."""
    if sys.platform == 'win32':
        setup_gettext_win32()

def setup_gettext_win32():
    """Set up gettext environment for Win32"""
    for i in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
        if os.environ.get(i):
            break
    else:
        register_environ_win32()

def register_environ_win32():
    """Register gettext environment for Win32"""
    try:
        import ctypes
    except ImportError:
        pass
    else:
        lcid_user = ctypes.windll.kernel32.GetUserDefaultLCID()
        lcid_system = ctypes.windll.kernel32.GetSystemDefaultLCID()
        if lcid_user != lcid_system:
            lcid = [lcid_user, lcid_system]
        else:
            lcid = [lcid_user]
        import locale
        lang = [locale.windows_locale.get(i) for i in lcid]
        lang = ':'.join([i for i in lang if i])
        if lang:
            os.environ['LANGUAGE'] = lang

def datetime_to_integer(datetime):
    """Convert datetime object to integer value.
    'datetime' is the datetime object"""
    return time.mktime(datetime.timetuple())
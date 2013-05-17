#!/usr/bin/python

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
#    Copyright 2007 Alex Slesarev

"""setup.py
Installer module."""

import sys
import os
from distutils.core import setup

if sys.platform == 'win32':
    PY2EXE = __import__('py2exe')

#
# hack to deal w/ fact distutils won't
# allow us to set absolute path prefix
# on windows
#

if not 'sdist' in sys.argv:
    SETUPCFG = "setup.cfg.in"
    # Was setup.cfg specified on the command line?
    try:
        SETUP_INDEX = sys.argv.index('--setup-cfg')
        SETUPCFG = sys.argv[SETUP_INDEX + 1]
        sys.argv.pop(SETUP_INDEX)
        sys.argv.pop(SETUP_INDEX)
    except ValueError:
        print "There is no parameters for installer"

    if sys.platform != 'win32':
        os.system ("""cp %(SETUPCFG)s setup.cfg""" % locals())
    else:
        try:
            os.remove('setup.cfg')
        except OSError:
            print "Can't remove setup.cfg"

MAILDISPATCHER_DATA = [
    ('maildispatcher/glade',
        ['share/maildispatcher/glade/maildispatcher.glade']),
    ('maildispatcher/i18n/ru/LC_MESSAGES',
        ['share/maildispatcher/i18n/ru/LC_MESSAGES/maildispatcher.mo'])]

if sys.platform != 'win32':
    MAILDISPATCHER_DATA.append(('/usr/share/applications',
                                ['maildispatcher.desktop']))

PY2EXE_OPTS = {
    "py2exe": {
        'includes': 'pango,atk,gobject, cairo, pangocairo',
        "dll_excludes": [
        "iconv.dll","intl.dll","libatk-1.0-0.dll",
        "libgdk_pixbuf-2.0-0.dll","libgdk-win32-2.0-0.dll",
        "libglib-2.0-0.dll","libgmodule-2.0-0.dll",
        "libgobject-2.0-0.dll","libgthread-2.0-0.dll",
        "libgtk-win32-2.0-0.dll","libpango-1.0-0.dll",
        "libpangowin32-1.0-0.dll"],
        }
    }

setup(
    name = 'maildispatcher',
    description = 'A tool for dispatching (basically, deleting) email '
        'messages on POP3 server via Plain or SSL connection with advanced '
        'filtering capabilities.',
    long_description = 'A tool for dispatching (basically, deleting) email '
        'messages on POP3 server via Plain or SSL connection with advanced '
        'filtering capabilities.',
    url = 'http://maildispatcher.sourceforge.net/',
    author = "Alex Slesarev",
    author_email = 'nuald@users.sourceforge.net',
    license = 'GPL',
    version = '0.3',
    packages = ['maildispatcher'],
    package_dir =
        { 'maildispatcher' : 'share/maildispatcher/lib/maildispatcher' },
    data_files = MAILDISPATCHER_DATA,
    scripts = ['bin/maildispatcher'],
    windows = ['bin/maildispatcher'],
    options = PY2EXE_OPTS,
)

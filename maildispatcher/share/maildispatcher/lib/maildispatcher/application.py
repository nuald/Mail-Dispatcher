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

"""application.py
Mail dispatcher main module."""

from . import SHARED_FILES
from os import path
import gtk
import sys
from mainwindowcontroller import MainWindowController
from calendarwindowcontroller import CalendarWindowController

def main():
    """ Entry point to the program. """
    gtk.gdk.threads_init()
    glade_path = unicode(
                    path.join(SHARED_FILES, 'glade', 'maildispatcher.glade'),
                    sys.getfilesystemencoding())
    calendar_window_controller = CalendarWindowController(glade_path, 
                                                          'calendar_window')
    MainWindowController(glade_path, 'main_window', calendar_window_controller)
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

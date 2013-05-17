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


"""calendarwindowcontroller.py
Glade wrapper for calendar window."""

#TODO: add support for keyboard navigation

import datetime
from gladebase import UI, Controller

class CalendarWindowController(Controller):
    """ Glade tree for calendar window. """

    def __init__(self, glade_file, calendar_window_name):
        """Initialize calendar window tree class instance.
        'glade_file' is the file name of required Glade file.
        'calendar_window_name' is the name of the calendar window widget."""
        self.on_calendar_double_click = \
            lambda calendar: self._set_date_to_btn(calendar)
        self.on_cancel_button_clicked = lambda button: self.close()
        Controller.__init__(self, UI(glade_file, calendar_window_name))
        self.update_date = lambda: False
        self.set_btn_active = lambda: False

    def on_ok_button_clicked(self, _button):
        """Handler for OK button.
        'button' is the OK button control."""
        self._set_date_to_btn(self.gui.calendar)
        
    def setup_callbacks(self, update_date, set_btn_active):
        """Set callbacks from main window.
        'update_date' is the callback for update date buttons labels.
        'set_btn_active' is the callback for setting date buttons sensitivity"""
        self.update_date = update_date
        self.set_btn_active = set_btn_active

    def close(self, reset_active = True):
        """Close calendar window.
        'reset_active' is reset active state of button"""
        self.gui.calendar_window.hide()
        if reset_active:
            self.set_btn_active(False)

    def show(self, button):
        """Show calendar window.
        'button' is the widget aside which window is shown"""
        rect = button.get_allocation()
        origin_x, origin_y = button.window.get_origin()
        cal_width = self.gui.calendar_window.get_size()[0]
        self.gui.calendar_window.move(
                                origin_x + rect.x - cal_width + rect.width,
                                origin_y + rect.y + rect.height)
        self.gui.calendar_window.show()
        self.gui.calendar_window.move(
                                origin_x + rect.x - cal_width + rect.width, 
                                origin_y + rect.y + rect.height)

    def on_clear_button_clicked(self, _button):
        """Handler for 'Clear' button.
        '_button' is the 'Clear' button control."""
        self.update_date(None)
        self.close()

    def on_set_current_button_clicked(self, _button):
        """Handler for 'Set Current Date' button.
        '_button' is the 'Set Current Date' button control."""
        self.gui.calendar.freeze()
        now = datetime.datetime.now()
        self.gui.calendar.select_month(now.month - 1, now.year)
        self.gui.calendar.select_day(now.day)
        self.gui.calendar.thaw()

    def _set_date_to_btn(self, calendar):
        """Update date label on button.
        'calendar' is the calendar widget control."""
        (year, month, day) = calendar.get_date()
        self.update_date(datetime.datetime(year, month + 1, day))
        self.close()

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

"""cellrenderertimestamp.py
Renderer for time stamp values."""

import gtk, gobject
import pango
import datetime
import sys

# gtk.GenericCellRenderer provide too many public methods
class CellRendererTimeStamp(gtk.GenericCellRenderer):# pylint: disable-msg=R0904
    """Class-renderer for time stamp values."""

    __gproperties__ = {
        'text': (gobject.TYPE_INT, 'text', 'text', -sys.maxint, 
                 sys.maxint, 0, gobject.PARAM_READWRITE),
    }

    def __init__(self):
        self.__gobject_init__()
        gtk.GenericCellRenderer.__init__(self)
        self.text = None

    def do_set_property(self, pspec, value):
        """Set property.
        'pspec' is the property name.
        'value' is the property value."""
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        """Get property.
        'pspec' is the property name."""
        return getattr(self, pspec.name)

    def _get_string(self):
        """Get displayed string."""
        if self.text and self.text != -1:
            value = datetime.datetime.fromtimestamp(self.text)
            return value.strftime('%c')
        return ''

    def on_render(self, window, widget, _ba, cell, _ea, flags):#IGNORE:R0913
        """Renderer callback.
        'window' is the drawing window.
        'widget' is the drawing widget.
        '_ba' is the background area.
        'cell' is the cell area.
        '_ea' is the expose area.
        'flags' is the drawing flags."""
        if self.text and self.text != -1:
            layout = widget.create_pango_layout(self._get_string())
            attrs = pango.AttrList()
            color = widget.style.text[0]
            if flags & gtk.CELL_RENDERER_SELECTED:
                color = widget.style.white
            attrs.insert(pango.AttrForeground(color.red, color.green, 
                                                  color.blue, 0, -1))
            layout.set_attributes(attrs)
            window.draw_layout(widget.style.black_gc, cell.x, cell.y, layout)

    def on_get_size(self, widget, _cell_area):
        """Calculate required size.
        'widget' is the drawing widget.
        'cell_area' is the drawing cell area."""
        if not self.text:
            return 0, 0, 0, 0
        layout = widget.create_pango_layout(self._get_string())
        width, height = layout.get_pixel_size()
        return 0, 0, width, height

gobject.type_register(CellRendererTimeStamp)

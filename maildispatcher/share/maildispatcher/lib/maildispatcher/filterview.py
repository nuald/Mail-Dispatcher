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

"""filterview.py
Filters view for mail dispatcher."""

import gtk

class FilterView:
    """ View for displaying filters headers and all related UI. """
    
    def __init__(self):
        """ Sets up and populates our gtk.TreeView. """
        self.renderer_field = gtk.CellRendererText()
        self.renderer_text = gtk.CellRendererText()
        self.field_column = gtk.TreeViewColumn(_('Field'), self.renderer_field)
        self.text_column = gtk.TreeViewColumn(_('Text'), self.renderer_text)
        return
    
    @staticmethod
    def setup_column(column, renderer, model_column):
        """Set up a text column.
        'column' is the setting up column.
        'renderer' is the renderer for the column.
        'model_column' is the corresponding model for the column."""
        column.add_attribute(renderer, 'text', model_column)
        column.set_sort_column_id(model_column)
    
    @staticmethod
    def change_text(renderer, path, text, model, column):
        """Change text of filter handler.
        'renderer' is the renderer of the column.
        'path' is the path in the model for the column.
        'text' is a new text for the column.
        'model' is the model of the column.
        'column' is the current column."""
        if text:
            iterator = model.get_iter_from_string(path)
            model.set_value(iterator, column, text)
        
    def make_view(self, model, view):
        """Displays the model in a view.
        'model' is the model for the filter view.
        'view' is the view of the filter view."""
        view.set_model(model)

        self.setup_column(self.field_column, self.renderer_field, 0)
        self.setup_column(self.text_column, self.renderer_text, 1)
        self.renderer_text.set_property('editable', True)
        self.renderer_text.connect('edited', self.change_text, model, 1)
        
        view.append_column(self.field_column)
        view.append_column(self.text_column)

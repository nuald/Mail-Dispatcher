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

"""headersview.py
Display view for email headers."""

import gtk
import pango
from cellrenderertimestamp import CellRendererTimeStamp
from appregistry import AppRegistry

class HeadersView:
    """ View for displaying email headers and all related UI. """

    # Helper class without many public methods
    class RendererHelper:# pylint: disable-msg=R0903
        """ Renderers used for column rendering. """
        
        def __init__(self):
            self.text_renderer = gtk.CellRendererText()
            self.text_renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
            self.toggle_renderer = gtk.CellRendererToggle()
            self.toggle_renderer.set_property('activatable', True)
    
    def __init__(self):
        """ Sets up and populates our gtk.TreeView. """
        self.renderers = HeadersView.RendererHelper()
        self.delete_column = gtk.TreeViewColumn(_('Delete'),
                                                self.renderers.toggle_renderer)
        self.from_column = gtk.TreeViewColumn(_('From'),
                                              self.renderers.text_renderer)
        self.to_column = gtk.TreeViewColumn(_('To'),
                                            self.renderers.text_renderer)
        self.date_column = gtk.TreeViewColumn(_('Date'), 
                                              CellRendererTimeStamp())
        self.size_column = gtk.TreeViewColumn(_('Size'),
                                              self.renderers.text_renderer)
        self.subj_column = gtk.TreeViewColumn(_('Subj'),
                                              self.renderers.text_renderer)
        return

    @staticmethod
    def column_clicked(column, column_id):
        """Handler for column header clicking.
        'column' is the current column.
        'column_id' is the column id in the model."""
        headers_model = AppRegistry.get_instance().get_headers_model()
        model = headers_model.tree_model
        tree_store = model.get_model()
        column.set_sort_indicator(True)
        if not column.get_sort_indicator():
            column.set_sort_indicator(True)
            column.set_sort_order(gtk.SORT_ASCENDING)
            tree_store.set_sort_column_id(column_id, gtk.SORT_ASCENDING)
        else :
            if column.get_sort_order() == gtk.SORT_ASCENDING :
                column.set_sort_order(gtk.SORT_DESCENDING)
                tree_store.set_sort_column_id(column_id, gtk.SORT_DESCENDING)
            else :
                column.set_sort_order(gtk.SORT_ASCENDING)
                tree_store.set_sort_column_id(column_id, gtk.SORT_ASCENDING)
    
    def setup_column(self, column, size, model_column, renderer = None):
        """Setup column's style.
        'column' is the setting up column.
        'size' is the new size of the column.
        'model_column' is the model for the column."""
        column.set_resizable(True)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(size)
        column.add_attribute(renderer or self.renderers.text_renderer, 'text',
                             model_column)
        column.set_property('clickable', True)
        column.connect('clicked', self.column_clicked, model_column)
    
    def make_view(self, view, update_func):
        """Displays the model in a view.
        'model' is the model of email headers.
        'view' is the view of the model.
        'update_func' is the callback for updating main window.
        'columns' is the list of the required columns."""
        headers_model = AppRegistry.get_instance().get_headers_model()
        model = headers_model.tree_model
        columns = headers_model.columns
        view.set_model(model)
        
        self.renderers.toggle_renderer.connect('toggled', self.col1_toggled_cb,
                               columns['delete'], update_func)
        self.delete_column.add_attribute(self.renderers.toggle_renderer,
                                         'active', columns['delete'])

        self.setup_column(self.from_column, 150, columns['from'])
        self.setup_column(self.to_column, 100, columns['to'])
        self.setup_column(self.size_column, 100, columns['size'])
        self.setup_column(self.subj_column, 200, columns['subj'])
        
        dt_renderer = CellRendererTimeStamp()
        self.date_column.pack_start(dt_renderer, True)
        self.setup_column(self.date_column, 100, columns['date'], dt_renderer)
        
        view.append_column(self.delete_column)
        view.append_column(self.subj_column)
        view.append_column(self.from_column)
        view.append_column(self.date_column)
        view.append_column(self.size_column)
        view.append_column(self.to_column)

    @staticmethod
    def col1_toggled_cb(cell, path, del_column, update):
        """Sets the toggled state on the toggle button to true or false.
        'cell' is the clicked cell.
        'path' is the path of the cell.
        'del_column' is the id of delete column."""
        headers_model = AppRegistry.get_instance().get_headers_model()
        virtual_model = headers_model.tree_model
        model = virtual_model.get_model()
        real_path = virtual_model.convert_path_to_child_path(path)
        if real_path:
            model[real_path][del_column] = not model[real_path][del_column]
            update()

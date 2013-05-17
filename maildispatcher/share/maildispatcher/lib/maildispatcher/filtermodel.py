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

"""filtermodel.py
Model for filter."""

import gtk, gobject

class FilterModel:
    """ The filter model class is the model for filtering headers. """

    def __init__(self, filter_type):
        """Sets up and populates our gtk.TreeStore.
        'filter_type' is the filter type (True - deletion, False - storing)"""
        self.tree_store = gtk.TreeStore(gobject.TYPE_STRING, 
                                        gobject.TYPE_STRING)
        self.current_path = None
        self.filter_type = filter_type
        self.update_func = lambda: False 
    
    def add_entry(self, field, text, do_update = True):
        """Add new entry in filters.
        'field' is the type of filter.
        'text' is the text of filter."""
        self.tree_store.append(None, (field, text))
        if do_update:
            self.update_func()
    
    def delete_current_entry(self):
        """ Delete an current entry from filter. """
        entry_iter = self.tree_store.get_iter(self.current_path)
        self.tree_store.remove(entry_iter)
        self.update_func()

    def get_storage(self):
        """ Get model as array of tuples. """
        storage = []
        self.tree_store.foreach(
            lambda model, _path, iterator, storage: storage.append(
                (model.get_value(iterator, 0), model.get_value(iterator, 1))),
            storage)
        return storage
    
    def load_storage(self, storage):
        """Load model as array of tuples.
        'storage' is the loaded storage for the model."""
        self.tree_store.clear()
        for field, text in storage:
            self.add_entry(field, text, False)
        self.update_func()

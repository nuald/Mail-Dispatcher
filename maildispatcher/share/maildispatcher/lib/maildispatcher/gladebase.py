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


"""gladebase.py
This module provides base classes for Glade-derived UIs and their
controllers."""

import os, gtk, utils

# Helper class without many public methods
class UI(gtk.glade.XML):# pylint: disable-msg=R0903
    """Base class for UIs loaded from glade."""
    
    def __init__(self, filename, rootname, glade_dir="."):
        """Initialize a new instance.
        'filename' is the name of the .glade file containing the UI hierarchy.
        'rootname' is the name of the topmost widget to be loaded.
        'gladeDir' is the name of the directory, relative to the Python
        path, in which to search for `filename'."""
        if glade_dir:
            filename = os.path.join(glade_dir, filename)
        self._glade_path_name = utils.find(filename)
        
        gtk.glade.XML.__init__(self, self._glade_path_name, rootname)
        self.root = self.get_widget(rootname)

    def __getattr__(self, name):
        """Look up an as-yet undefined attribute, assuming it's a widget."""
        result = self.get_widget(name)
        if result is None:
            raise AttributeError(
                _("Can't find widget %(name)s in %(pathname)s.\n") %
                            {'name':name, 'pathname':self._glade_path_name})
        
        # Cache the widget to speed up future lookups.  If multiple
        # widgets in a hierarchy have the same name, the lookup
        # behavior is non-deterministic just as for libglade.
        setattr(self, name, result)
        return result

class Controller:
    """Base class for all controllers of glade-derived UIs."""
    def __init__(self, gui):
        """Initialize a new instance.
        'user_interface' is the user interface to be controlled."""
        self.gui = gui
        self.gui.signal_autoconnect(self.get_all_methods())

    def get_all_methods(self):
        """Get a dictionary of all methods in self's class hierarchy."""
        result = {}

        # Find all callable instance/class attributes.  This will miss
        # attributes which are "interpreted" via __getattr__.  By
        # convention such attributes should be listed in
        # self.__methods__.
        all_attr_names = self.__dict__.keys() + self.get_all_class_attributes()
        for name in all_attr_names:
            value = getattr(self, name)
            if callable(value):
                result[name] = value
        return result

    def get_all_class_attributes(self):
        """Get a list of all attribute names in self's class hierarchy."""
        name_set = {}
        for current_class in self.get_all_classes():
            name_set.update(current_class.__dict__)
        result = name_set.keys()
        return result

    def get_all_classes(self):
        """Get all classes in self's heritage."""
        result = [self.__class__]
        i = 0
        while i < len(result):
            current_class = result[i]
            result.extend(list(current_class.__bases__))
            i = i + 1
        return result

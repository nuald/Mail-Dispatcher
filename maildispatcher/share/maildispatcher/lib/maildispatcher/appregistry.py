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

"""appregistry.py
Registry for all models in the application."""

class AppRegistry:
    """Class holding all required models."""
    # Create a class variable that will hold a reference
    # to the single instance of TestSingleton.
    instance = None

    #Helper class with limited functionality
    class AppRegistryHelper:# pylint: disable-msg=R0903
        """Helper class that will override the __call___
        method in order to provide a factory method for AppRegistry."""
        
        def __init__(self):
            pass
        
        @staticmethod
        def __call__(*_args, **_params):
            # If an instance of AppRegistry does not exist,
            # create one and assign it to AppRegistry._instance.
            if not AppRegistry.instance:
                AppRegistry.instance = AppRegistry()
            
            # Return AppRegistry._instance, which should contain
            # a reference to the only instance of AppRegistry
            # in the system.
            return AppRegistry.instance
    
    # Create a class level method that must be called to
    # get the single instance of TestSingleton.
    get_instance = AppRegistryHelper()

    # Initialize an instance of the TestSingleton class.
    def __init__(self):
        # Optionally, you could go a bit further to guarantee
        # that no one created more than one instance of TestSingleton:
        if AppRegistry.instance:
            raise RuntimeError, 'Only one instance of AppRegistry is allowed!'
        AppRegistry.instance = self
        self._headers_model = None
        self._deletion_filters_model = None
        self._storing_filters_model = None
        self._encoding_model = None
        
    def get_headers_model(self):
        """Get headers model."""
        if not self._headers_model:
            from headersmodel import HeadersModel
            self._headers_model = HeadersModel()
        return self._headers_model
    
    def get_deletion_filters(self):
        """Get deletion filters model."""
        if not self._deletion_filters_model:
            from filtermodel import FilterModel
            self._deletion_filters_model = FilterModel(True)
        return self._deletion_filters_model

    def get_storing_filters(self):
        """Get deletion filters model."""
        if not self._storing_filters_model:
            from filtermodel import FilterModel
            self._storing_filters_model = FilterModel(False)
        return self._storing_filters_model

    def get_encoding_model(self):
        """Get encoding model."""
        if not self._encoding_model:
            from encodingmodel import EncodingModel
            self._encoding_model = EncodingModel()
        return self._encoding_model

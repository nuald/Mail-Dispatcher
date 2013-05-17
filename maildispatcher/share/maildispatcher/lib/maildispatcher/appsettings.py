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

"""appsettings.py
Module for persistent storing of application settings."""

import os
import sys
import pickle
import utils
import appsecuresettings
from appregistry import AppRegistry

CONFIG_FILE = 'defaults.cfg'
DATA_DIR = 'maildispatcher'

def user_data_dir(appname):
    """ Return full path to the user-specific data dir for this application.
    'appname' is the name of application.
    
    Typical user data directories are:
        Windows:    C:\Documents and Settings\USER\Application Data\<appname>
        Mac OS X:   ~/Library/Application Support/<appname>
        Unix:       ~/.<lowercased-appname>
    """
    if sys.platform.startswith("win"):
        from ctypes import windll, create_unicode_buffer
        path_buffer = create_unicode_buffer('\0' * 1024)
        # CSIDL_APPDATA = 26
        result = windll.shell32.SHGetFolderPathW(0, 26, 0, 0, path_buffer)
        if not result:
            path = path_buffer.value
        else:
            path = os.path.join(os.path.expanduser('~'), 'Application Data')
        path = os.path.join(path, appname)
    elif sys.platform == 'darwin':
        carbon = __import__('Carbon')
        path = carbon.Folder.FSFindFolder(carbon.Folders.kUserDomain,
                                carbon.Folders.kApplicationSupportFolderType,
                                carbon.Folders.kDontCreateFolder)
        path = os.path.join(path.FSRefMakePath(), appname)
    else:
        path = os.path.expanduser('~/.' + appname.lower())
    return os.path.normpath(path)

def get_app_path():
    """ Get home directory. """
    config_dir = user_data_dir(DATA_DIR)
    if not os.path.exists(config_dir) :
        os.makedirs(config_dir)
    return os.path.normpath(os.path.join(config_dir, CONFIG_FILE))

def load_app_settings():
    """ Load setting from configuration file. """
    app_path = get_app_path()
    if not os.access(app_path, os.F_OK):
        return (None, None, None)
    pkl_file = open(app_path, 'rb')
    try :
        server_info = pickle.load(pkl_file)
        deletion_filters = pickle.load(pkl_file)
        storing_filters = pickle.load(pkl_file)
    except (EOFError, IndexError), ex:
        utils.print_exception(ex, _('Settings loading error'))
        return (None, None, None)
    finally:
        pkl_file.close()
    
    host, _connection_type, port = server_info
    user_info = appsecuresettings.get_credentials(host, port)
    return ((server_info, user_info), deletion_filters, storing_filters)

def save_app_settings(account_info):
    """Save settings to configuration file.
    'account_info' is the account information.
    'deletion_filters' is the list of deletion filters.
    'storing_filters' is the list of storing filters."""
    output = open(get_app_path(), 'wb')
    server_info, user_info = account_info
    host, _connection_type, port = server_info
    appsecuresettings.set_credentials(user_info, host, port)
    
    deletion_filters = AppRegistry.get_instance().get_deletion_filters()
    storing_filters = AppRegistry.get_instance().get_storing_filters()
    
    pickle.dump(server_info, output)
    pickle.dump(deletion_filters.get_storage(), output)
    pickle.dump(storing_filters.get_storage(), output)
    output.close()

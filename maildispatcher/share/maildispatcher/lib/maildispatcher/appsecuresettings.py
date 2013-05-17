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

"""appsecuresettings.py
Module for secured persistent storing of application settings."""

import utils
import sys

def get_unix_mgr(server, protocol):
    """Get secured manager for UNIX OS.
    'server' is the mail server name.
    'protocol' is the used POP3 connection protocol."""
    try :
        from gnomekeyringmgr import GnomeKeyringMgr
        return GnomeKeyringMgr('MailDispatcher', server, protocol)
    except ImportError, ex:
        utils.print_exception(ex, 
                              _('Secure storage manager initialization error'))
    return None
    
def get_secured_mgr(server, protocol):
    """Get secured manager.
    'server' is the mail server name.
    'protocol' is the used POP3 connection protocol."""
    if sys.platform.startswith('win') or sys.platform == 'darwin':
        return None
    return get_unix_mgr(server, protocol)

def get_credentials(server, protocol):
    """Load setting from secured storage.
    'server' is the mail server name.
    'protocol' is the used POP3 connection protocol."""
    mgr = get_secured_mgr(server, protocol)
    if mgr:
        return mgr.get_credentials()
    return ('', '')

def set_credentials(user_info, server, protocol):
    """Save settings to secured storage.
    'user_info' is the saved user information.
    'server' is the mail server name.
    'protocol' is the used POP3 connection protocol."""
    mgr = get_secured_mgr(server, protocol)
    if mgr:
        mgr.set_credentials(user_info)

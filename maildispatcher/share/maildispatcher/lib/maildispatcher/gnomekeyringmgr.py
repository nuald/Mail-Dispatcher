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

"""gnomekeyringmgr.py
Class for manipulating gnome keyring."""

import gnomekeyring as gkey
import utils

class GnomeKeyringMgr:
    """ Class for manipulating gnome keyring. """
    
    def __init__(self, name, server, protocol):
        """Initialize internal attributes.
        'name' is the name of corresponding secured storage.
        'server' is the mail server name.
        'protocol' is the used POP3 connection protocol."""
        self._name = name
        self._server = server
        self._protocol = protocol
        #self._keyring = gkey.get_default_keyring_sync()

    def get_credentials(self):
        """ Get credentials. """
        try:
            attrs = {'server': self._server, 'protocol': self._protocol}
            items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
            if items:
                return (items[0].attributes['user'], items[0].secret)
        except (gkey.DeniedError, gkey.NoMatchError), ex:
            utils.print_exception(ex, _('Checking credentials error'))
        return ('', '')

    def set_credentials(self, (user, pwd)):
        """Set credentials.
        'user' is the name of user's account.
        'pwd' is the password of user's account."""
        attrs = {'user': user,
                'server': self._server,
                'protocol': self._protocol }
        gkey.item_create_sync(gkey.get_default_keyring_sync(),
                gkey.ITEM_NETWORK_PASSWORD, self._name, attrs, pwd, True)

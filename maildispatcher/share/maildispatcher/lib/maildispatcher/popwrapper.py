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

"""popwrapper.py
Wrapper for working with POP3 server."""

import poplib

# How many lines of message body to retrieve
MAXLINES = 0

class PopWrapper:
    """ Wrapper for working with POP3 server."""
    
    def __init__(self, (server_info, user_info)):
        """Establish connection to POP3 server.
        'server_info' is the POP3 server information.
        'user_info' is the user's account information."""
        host, connection_type, port = server_info
        user, pwd = user_info
        if connection_type == 0 :
            self.pop = poplib.POP3(host, port)
        else :
            self.pop = poplib.POP3_SSL(host, port)
        self.pop.user(user)
        self.pop.pass_(pwd)
        _count, _bytes = self.pop.stat()
        # Print server information
        print _('Logged in as %(user)s@%(host)s') % locals()
        print _('Status: %(_count)d message(s), %(_bytes)d bytes') % locals()
    
    def delete_message(self, index):
        """Delete message.
        'index' is the index of deleted message."""
        self.pop.dele(index)
    
    def get_stat(self):
        """ Get statistics. """
        return self.pop.stat()
    
    def get_top(self, msgnum):
        """Get top lines.
        'msgnum' is the number of the message."""
        return self.pop.top(msgnum, MAXLINES)
    
    def get_msg(self, msgnum):
        """Get entire message and set 'seen' flag.
        'msgnum' is the number of the message."""
        return self.pop.retr(msgnum)
    
    def __del__(self):
        """ Commit operations and disconnect from server. """
        print _('Closing POP3 session')
        if hasattr(self, 'pop'):
            self.pop.quit()

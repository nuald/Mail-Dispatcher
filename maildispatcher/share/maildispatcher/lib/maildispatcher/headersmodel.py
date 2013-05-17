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

"""headersmodel.py
Model for email headers."""

import gtk
import re
import socket
import poplib
from popwrapper import PopWrapper
from utils import threaded, idlefunction, datetime_to_integer, print_exception
from email.header import decode_header
import time
from email.utils import parsedate
from email import message_from_string
from appregistry import AppRegistry

# Headers we're actually interested in
RX_FROM  = re.compile(r'^From: (.+)')
RX_TO  = re.compile(r'^To: (.+)')
RX_SUBJ  = re.compile(r'^Subject: (.+)')
RX_DATE = re.compile(r'^Date: (.+)')

class HeadersModel:
    """ Class for model for email headers."""

    #Helper class without many methods
    class TimestampHelper:# pylint: disable-msg=R0903
        """ Helper for working with timestamps. """
        
        def __init__(self):
            self.last_msg_date = -1
            self.low_bound = -1
            self.high_bound = -1
            self.downloaded = {}

    def __init__(self):
        """ Set up and populate our gtk.TreeStore. """
        columns_dict = (('number', int), ('from', str), ('to', str),
                        ('subj', str), ('date', int), ('size', str),
                        ('delete', 'gboolean'), ('visible', 'gboolean'))
        # Use magic for creating argument list
        self.tree_store = gtk.TreeStore( # pylint: disable-msg=W0142
            *([col_type for col_name, col_type in columns_dict]))
        self.tree_store.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.tree_model = self.tree_store.filter_new()
        self.columns = dict([(col_name, i) for i, (col_name, col_type)
                           in zip(xrange(len(columns_dict)), columns_dict)])
        self.tree_model.set_visible_column(self.columns['visible'])
        self.is_download_stopped = False
        self.is_deletion_stopped = False
        self.timestamp_helper = HeadersModel.TimestampHelper()

    def _get_msg_from_generator(self, generator, pop, messages_count, 
                                set_fraction):
        """Download headers from POP3 server using generator.
        'generator' is the used generator of indexes.
        'pop' is the connection instance to POP3 server.
        'messages_count' is the amount of messages for downloading.
        'time_period' is the required period of message's time.
        'set_fraction' is the callback for showing downloading progress."""
        for msgnum in generator:
            if self.is_download_stopped:
                return
            if not (msgnum in self.timestamp_helper.downloaded):
                _response, lines, octets = pop.get_top(msgnum)
                self._add_new_item(msgnum, lines, octets)
                self.timestamp_helper.downloaded[msgnum] = \
                    self.timestamp_helper.last_msg_date
            else:
                self.timestamp_helper.last_msg_date = \
                    self.timestamp_helper.downloaded[msgnum]
            set_fraction(1.0 * msgnum / messages_count)

    @staticmethod
    def _get_matched_string(regexp, lines):
        """Get matched string using regexp and decode it.
        'regexp' is the used regexp.
        'lines' is the processing lines."""
        line = ','.join([match.group(1) for match in 
                [regexp.match(item) for item in lines] if match])
        decoded_line, encoding = decode_header(line)[0]
        if encoding:
            return unicode(decoded_line, encoding)
        encoding_model = AppRegistry.get_instance().get_encoding_model()
        if encoding_model.current:
            try:
                return unicode(decoded_line, encoding_model.current)
            except (UnicodeDecodeError, LookupError), ex:
                print_exception('Header decoding error:', ex)
        return decoded_line

    @idlefunction
    def _add_new_item(self, msgnum, lines, octets):
        """Add new item to the headers view.
        'msgnum' is the number of the message.
        'lines' is the header of the message.
        'octets' is the size of the message"""
        from_part = self._get_matched_string(RX_FROM, lines)
        to_part = self._get_matched_string(RX_TO, lines)
        subj_part = self._get_matched_string(RX_SUBJ, lines)
        date_part = self._get_matched_string(RX_DATE, lines)
        self.timestamp_helper.last_msg_date = -1
        if date_part:
            date_int = time.mktime(parsedate(date_part))
            self.timestamp_helper.last_msg_date = date_int

        item = (('number', msgnum), ('from', from_part), ('to', to_part),
                ('subj', subj_part),
                ('date', self.timestamp_helper.last_msg_date), 
                ('size', octets), ('delete', False), ('visible', True))

        self.tree_store.append(None, tuple([item_val for _item_name, 
                                           item_val in item]))

    @threaded
    def download_headers(self, account, time_period, callbacks):
        """Download email headers from POP3 server.
        'account' is the user's account information.
        'time_period' is the required period of message's time.
        'callbacks' is the required callbacks for interaction with UI."""
        set_progressbar_text, set_progressbar_idle, \
            set_progressbar_fraction, stop_downloading, \
            show_error = callbacks
        try :
            pop = PopWrapper(account)
            stat = pop.get_stat()
            self.tree_store.clear()
            set_progressbar_text(_('Getting email headers...'))
            messages_count = stat[0]
            self._download_from_server(pop, messages_count, time_period,
                                       set_progressbar_fraction)
            set_progressbar_idle()
        except (socket.error, poplib.error_proto), ex:
            show_error(ex, _('Downloading headers error'))
        finally:
            stop_downloading()
    
    @threaded
    def delete_msgs(self, account, callbacks):
        """Delete messages from POP3 server.
        'account' is the user's account information.
        'callbacks' is the required callbacks for interaction with UI."""
        indexes = self.get_indexes_for_deletion()
        count = len(indexes)
        proceed_further = True
        set_progressbar_text, set_progressbar_idle, \
            set_progressbar_fraction, stop_deleting, \
            show_error = callbacks
        try :
            if count <= 0 : 
                return
            pop = PopWrapper(account)
            set_progressbar_text(_('Deleting email messages...'))
            self._delete_messages_from_server(pop, indexes, count, 
                                              set_progressbar_fraction)
            set_progressbar_idle()
        except (socket.error, poplib.error_proto), ex:
            proceed_further = False
            show_error(ex, _('Deleting messages error'))
        finally :
            stop_deleting(proceed_further)

    def download_msg(self, account, path, show_error):
        """Download selected message.
        'account' is the user's account information.
        'path' is the path to the required message.
        'show_error' is the callback for showing error."""
        try:
            pop = PopWrapper(account)
            iterator = self.tree_model.get_iter(path)
            index =  self.tree_model.get_value(iterator, self.columns['number'])
            _response, lines, _octets = pop.get_msg(index)
            mesg = '\n'.join(lines)
            encoding_model = AppRegistry.get_instance().get_encoding_model()
            charset = message_from_string(mesg).get_content_charset(
                encoding_model.current)
            try:
                result = unicode(mesg, charset)
            except (UnicodeDecodeError, LookupError):
                result = mesg
            return result
        except (socket.error, poplib.error_proto), ex:
            show_error(ex, _('Downloading error'))
            return ''
    
    def get_msg_counters(self):
        """ Get total messages and deleted messages. """
        del_indexes = self.get_indexes_for_deletion()
        hidden_indexes = self.get_hidden_indexes()
        return (len(del_indexes), len(hidden_indexes), len(self.tree_store))

    def get_indexes_for_deletion(self):
        """ Get all items' indexes marked for deletion. """
        indexes = []
        self.tree_store.foreach(self._match_deleted_items, indexes)
        return indexes
    
    def get_hidden_indexes(self):
        """ Get all items' indexes marked as hidden. """
        indexes = []
        self.tree_store.foreach(self._match_hidden_item, indexes)
        return indexes
    
    def clear_all(self):
        """ clear all items """
        self.tree_store.foreach(self._set_item_attr, False)
    
    def select_all(self):
        """ Clear all items. """
        self.tree_store.foreach(self._set_item_attr, True)
    
    def apply_filter(self, filter_model, is_delete):
        """Apply filter to current model.
        'filter_model' is the model of the required filter.
        'is_delete' is a flag of deletion (for True value) or 
        storing (for False value) for applied filters."""
        self.tree_store.foreach(self._match_filter, (filter_model, is_delete))
        self.tree_model.refilter()
        
    def _delete_messages_from_server(self, pop, indexes, count, set_fraction):
        """Delete messages from POP3 server.
        'pop' is the connection instance to POP3 server.
        'indexes' is the indexes of messages for deletion.
        'count' is the amount of messages for deletion.
        'set_fraction' is the callback for showing deletion progress."""
        for num in xrange(count):
            if self.is_deletion_stopped:
                break
            pop.delete_message(indexes[num])
            set_fraction(1.0 * num / count)

    def _bound_searcher(self, messages_count, date):
        """Find closest bounds to the date.
        'message_count' is the message count.
        'date' is the required date."""
        counter = 1
        required_date = datetime_to_integer(date)
        self.timestamp_helper.low_bound = 1
        self.timestamp_helper.high_bound = messages_count
        self.timestamp_helper.last_msg_date = -1
        diff = 1
        while True:
            yield counter
            if self.timestamp_helper.last_msg_date == -1:
                counter += 1
                diff += 1
                if counter > messages_count:
                    break
                continue
            if self.timestamp_helper.last_msg_date < required_date:
                self.timestamp_helper.low_bound = counter
                counter = (counter + self.timestamp_helper.high_bound) / 2
            if self.timestamp_helper.last_msg_date > required_date:
                self.timestamp_helper.high_bound = counter
                counter = (counter + self.timestamp_helper.low_bound) / 2
            if self.timestamp_helper.high_bound - \
                self.timestamp_helper.low_bound <= diff:
                return

    def _bin_searcher(self, phase, messages_count, date_from, date_to):
        """Generator used for binary searches of messages.
        'message_count' is the message count.
        'date_from' is the beginning of required date interval.
        'date_to' is the ending of required date interval."""
        generator = []
        if date_from == None and date_to == None:
            if phase == 0:
                generator = xrange(1, messages_count + 1)
            return generator
        if date_from == None:
            if phase == 0:
                generator = self._bound_searcher(messages_count + 1, date_to)
            if phase == 1:
                generator = xrange(1, self.timestamp_helper.high_bound)
            return generator
        if date_to == None:
            if phase == 0:
                generator = self._bound_searcher(messages_count + 1, date_from)
            if phase == 1:
                generator = xrange(self.timestamp_helper.low_bound,
                                   messages_count + 1)
            return generator
        if phase == 0:
            generator = self._bound_searcher(messages_count + 1, date_from)
        if phase == 1:
            generator = self._bound_searcher(messages_count + 1, date_to)
        if phase == 2:
            generator = xrange(self.timestamp_helper.low_bound,
                               self.timestamp_helper.high_bound)
        return generator

    def _download_from_server(self, pop, messages_count, time_period, 
                              set_fraction):
        """Download headers from POP3 server.
        'pop' is the connection instance to POP3 server.
        'messages_count' is the amount of messages for downloading.
        'time_period' is the required period of message's time.
        'set_fraction' is the callback for showing downloading progress."""
        use_date_interval, date_from, date_to = time_period
        generator = []
        self.timestamp_helper.downloaded = {}
        if use_date_interval:
            first_generator = self._bin_searcher(0, messages_count, 
                                                 date_from, date_to)
            self._get_msg_from_generator(first_generator, pop, messages_count, 
                                     set_fraction)
            low_bound = self.timestamp_helper.low_bound
            second_generator = self._bin_searcher(1, messages_count, 
                                                 date_from, date_to)
            self._get_msg_from_generator(second_generator, pop, messages_count,
                                     set_fraction)
            self.timestamp_helper.low_bound = low_bound
            third_generator = self._bin_searcher(2, messages_count, 
                                                 date_from, date_to)
            self._get_msg_from_generator(third_generator, pop, messages_count, 
                                     set_fraction)
        else:
            generator = xrange(1, messages_count + 1)
            self._get_msg_from_generator(generator, pop, messages_count, 
                                     set_fraction)

    def check_for_assurance(self, show_del_confirmation):
        """Ask user about his assurance to delete messages.
        'show_del_confirmation' is callback for showing delete confirmation."""
        indexes = self.get_indexes_for_deletion()
        delete_count = len(indexes)
        if delete_count > 0:
            total_count = len(self.tree_store)
            result = show_del_confirmation(delete_count, total_count)
            return result
        return True
    
    def _match_deleted_items(self, model, _path, iterator, data):
        """Search for items marked for deletion.
        'model' is the model for headers.
        '_path' is the current path of the model.
        'iterator' is the current iterator of the model.
        'data' is the custom data reference for manipulation."""
        if model.get_value(iterator, self.columns['delete']) == True:
            data.append(model.get_value(iterator, self.columns['number']))
        return False     # keep the foreach going
    
    def _match_hidden_item(self, model, _path, iterator, data):
        """Search for items marked as hidden.
        'model' is the model for headers.
        '_path' is the current path of the model.
        'iterator' is the current iterator of the model.
        'data' is the custom data reference for manipulation."""
        if model.get_value(iterator, self.columns['visible']) == False:
            data.append(model.get_value(iterator, self.columns['number']))
        return False     # keep the foreach going

    def _iterate_filter(self, model, _path, iterator, data):
        """Search fields for each filter.
        'model' is the model for headers.
        '_path' is the current path of the model.
        'iterator' is the current iterator of the model.
        'data' is the custom data reference for manipulation."""
        headers_model = self.tree_store
        field_part = model.get_value(iterator, 0)
        searched_text = model.get_value(iterator, 1).lower()
        headers_iter, is_delete = data
        
        parts = {_('From'): 'from', _('To'): 'to', _('Subject'): 'subj'}
        column = parts.get(field_part)
        if column and searched_text in headers_model.get_value(headers_iter, 
                                                self.columns[column]).lower():
            headers_model.set_value(headers_iter, self.columns['delete'],
                                    is_delete)
            if not is_delete :
                headers_model.set_value(headers_iter,
                                        self.columns['visible'], False) 
        return False
    
    def _match_filter(self, model, _path, iterator, (filter_model, is_delete)):
        """Search for items matched filter.
        'model' is the model for headers.
        '_path' is the current path of the model.
        'iterator' is the current iterator of the model.
        'filter_model' is the model of applied filter.
        'is_delete' is a flag of filter's type."""
        model.set_value(iterator, self.columns['visible'], True)
        filter_model.tree_store.foreach(self._iterate_filter, 
                                         (iterator, is_delete))
        return False     # keep the foreach going
    
    def _set_item_attr(self, model, _path, iterator, data):
        """Set item's delete attribute.
        'model' is the model for headers.
        '_path' is the current path of the model.
        'iterator' is the current iterator of the model.
        'data' is the custom data reference for manipulation."""
        if model.get_value(iterator, self.columns['visible']) == True :
            model.set_value(iterator, self.columns['delete'], data)

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


"""mainwindowcontroller.py
Glade wrapper for main window."""

import gtk
import datetime
from utils import idlefunction, print_exception, datetime_to_integer
from filterview import FilterView
from headersview import HeadersView
import appsettings
from gladebase import UI, Controller
from appregistry import AppRegistry

DELETION_FILTER = 0
STORING_FILTER = 1

class MainWindowController(Controller):
    """ Glade tree for main window. """

    def __init__(self, glade_file, main_window_name,
                 calendar_window_controller):
        """Initialize main window.
        'glade_file' is the name of the required Glade file.
        'main_window_name' is the name of the Main Windows widget.
        'calendar_window_tree' is the instance of calendar windows object."""
        Controller.__init__(self, UI(glade_file, main_window_name))

        tree_store = gtk.TreeStore(str, str)
        tree_store.append(None, ('Plain', '110'))
        tree_store.append(None, ('SSL', '995'))
        tree_store.append(None, ('TLS', '110'))
        self.gui.connection_combo.set_model(tree_store)

        self._is_downloading_headers = False
        self._load_app_settings()
        self._setup_filters()

        self.calendar_window_controller = calendar_window_controller
        self.process_date_toggle = True

        now = datetime.datetime.now()
        self.date_from = datetime_to_integer(now)
        self.date_to = datetime_to_integer(now)
        self._update_datetime_from(now)
        self._update_datetime_to(now)

        self.gui.add_filter_button.set_sensitive(False)
        self.gui.clear_all_button.set_sensitive(False)
        self.gui.select_all_button.set_sensitive(False)
        self.gui.preview_button.set_sensitive(False)

        self.gui.filter_type_combo.set_active(0)
        self.gui.filter_field_combo.set_active(0)

        encoding_model = AppRegistry.get_instance().get_encoding_model()
        self.gui.encoding_combo.set_model(encoding_model.store)
        self.gui.encoding_combo.set_text_column(1)
        self.gui.encoding_combo.set_active_iter(encoding_model.current)

        HeadersView().make_view(self.gui.headers_view, self.update_status)

    @staticmethod
    def on_encoding_combo_changed(combo):
        """Handler for changing encoding type.
        'combo' is the corresponding combobox."""
        encoding_model = AppRegistry.get_instance().get_encoding_model()
        iterator = combo.get_active_iter()
        text = None
        if iterator:
            text = encoding_model.store[iterator][0]
        text = text or combo.get_active_text()
        encoding_model.current = text

    def on_filter_text_entry_changed(self, entry):
        """Handler for changing new filter text.
        'entry' is the corresponding entry for text."""
        self.gui.add_filter_button.set_sensitive(bool(entry.get_text()))

    def on_filter_field_combo_changed(self, combo):
        """Handler for changing new filter type.
        'combo' is the corresponding combobox."""
        self._update_text_field(combo, self.gui.headers_view)

    def on_main_window_destroy(self, app):
        """Handler for closing application.
        'app' is the current application."""
        headers_model = AppRegistry.get_instance().get_headers_model()
        headers_model.is_deletion_stopped = True
        headers_model.is_download_stopped = True
        appsettings.save_app_settings(self._get_account_info())
        gtk.main_quit(app)

    def on_refresh_button_clicked(self, button):
        """Handler for Refresh button click.
        'button' is the Refresh button control."""
        label = button.get_label()
        if label == 'gtk-refresh':
            self._refresh_messages()
        elif label == 'gtk-stop':
            self._stop_refreshing(False)

    def on_connection_combo_changed(self, combo):
        """Handler for changing connection type.
        'combo' is the 'Connection Type' combobox control."""
        connection_type = combo.get_active_iter()
        port = self.gui.port_entry
        port.set_text(combo.get_model()[connection_type][1])

    def on_headers_view_cursor_changed(self, tree):
        """Handler for changed current row in headers.
        'tree' is the headers tree control."""
        self.gui.preview_button.set_sensitive(True)
        self._update_text_field(self.gui.filter_field_combo, tree)

    def on_add_filter_button_clicked(self, _button):
        """Handler for 'Add New Filter' button clicked.
        '_button' is the 'Add New Filter' button control."""
        field = self.gui.filter_field_combo.get_active_text()
        text = self.gui.filter_text_entry.get_text()
        filter_type = self.gui.filter_type_combo.get_active()
        if filter_type == DELETION_FILTER:
            model = AppRegistry.get_instance().get_deletion_filters()
            model.add_entry(field, text)
        elif filter_type == STORING_FILTER:
            model = AppRegistry.get_instance().get_storing_filters()
            model.add_entry(field, text)

    def _get_model_for_button(self, button):
        """Get model from button instance
        'button' is the corresponding button"""
        model = None
        deletion_filters_buttons = [self.gui.delete_deletion_filter_button,
                                   self.gui.apply_deletion_filters_button,
                                   self.gui.edit_deletion_filter_button]
        storing_filters_buttons = [self.gui.delete_storing_filter_button,
                                   self.gui.apply_storing_filters_button,
                                   self.gui.edit_storing_filter_button]
        if button in deletion_filters_buttons:
            model = AppRegistry.get_instance().get_deletion_filters()
        elif button in storing_filters_buttons:
            model = AppRegistry.get_instance().get_storing_filters()
        return model

    def on_delete_filter_button_clicked(self, button):
        """Handler for delete filter buttons clicked.
        'button' is the delete filter button control."""
        model = self._get_model_for_button(button)
        if model:
            model.delete_current_entry()
            self._apply_filter(model, model.filter_type)

    def on_filters_view_cursor_changed(self, filter_view):
        """Handler for changing current row in the filter.
        'filter_view' is the filter widget control."""
        path = filter_view.get_cursor()[0]
        model = None
        if filter_view is self.gui.deletion_filters_view:
            model = AppRegistry.get_instance().get_deletion_filters()
            self.gui.delete_deletion_filter_button.set_sensitive(True)
            self.gui.edit_deletion_filter_button.set_sensitive(True)
        elif filter_view is self.gui.storing_filters_view:
            model = AppRegistry.get_instance().get_storing_filters()
            self.gui.delete_storing_filter_button.set_sensitive(True)
            self.gui.edit_storing_filter_button.set_sensitive(True)
        if model:
            model.current_path = path

    def on_apply_filters_button_clicked(self, button):
        """Handler for apply filter buttons.
        'button' is the Apply button control."""
        model = self._get_model_for_button(button)
        if model:
            self._apply_filter(model, model.filter_type)

    def on_select_all_button_clicked(self, _button):
        """'Select All' clicked handler.
        '_button' is the 'Select All' button control."""
        headers_model = AppRegistry.get_instance().get_headers_model()
        headers_model.select_all()
        self.update_status()

    def on_clear_all_button_clicked(self, _button):
        """'Clear All' clicked handler.
        '_button' is the 'Clear All' button control."""
        headers_model = AppRegistry.get_instance().get_headers_model()
        headers_model.clear_all()
        self.update_status()

    def on_account_entry_changed(self, entry):
        """Check for empty values in connection settings.
        'entry' is the current validated entry."""
        refresh_button = self.gui.refresh_button
        if entry and not entry.get_text():
            refresh_button.set_sensitive(False)
            return
        is_empty = self.gui.host_entry.get_text()
        is_empty = is_empty and self.gui.user_entry.get_text()
        is_empty = is_empty and self.gui.password_entry.get_text()
        is_empty = is_empty and self.gui.port_entry.get_text()
        refresh_button.set_sensitive(bool(is_empty))

    def on_preview_button_clicked(self, _button):
        """Preview current message.
        '_button' is the 'Preview' button control."""
        path = self.gui.headers_view.get_cursor()[0]
        if path:
            headers_model = AppRegistry.get_instance().get_headers_model()
            msg = headers_model.download_msg(self._get_account_info(), path,
                  self._show_error)
            if msg:
                self._show_message(msg)

    def on_edit_filter_button_clicked(self, button):
        """Change filter.
        'button' is 'Edit Filter' button control."""
        treeview = None
        if button is self.gui.edit_deletion_filter_button:
            treeview = self.gui.deletion_filters_view
        elif button is self.gui.edit_storing_filter_button:
            treeview = self.gui.storing_filters_view
        if treeview:
            (path, column) = treeview.get_cursor()
            treeview.set_cursor(path, column, True)

    def _reset_calendar_window(self, button):
        """Reset calendar window.
        'button' is the current toggled button."""
        self.process_date_toggle = False
        self.calendar_window_controller.close(False)
        buttons = [self.gui.date_from_button, self.gui.date_to_button]
        for each_button in buttons:
            if not (each_button is button):
                each_button.set_active(False)
        self.process_date_toggle = True

    def on_date_from_button_toggled(self, button):
        """Change date/time for getting headers since.
        'button' is the button control for changing date."""
        if self.process_date_toggle:
            self.calendar_window_controller.setup_callbacks(
                                        self._update_datetime_from,
                                        self.gui.date_from_button.set_active)
            self._reset_calendar_window(button)
            if button.get_active():
                self.calendar_window_controller.show(button)

    def on_date_to_button_toggled(self, button):
        """Change date/time for getting headers since.
        'button' is the button control for changing date."""
        if self.process_date_toggle:
            self.calendar_window_controller.setup_callbacks(
                                        self._update_datetime_to,
                                        self.gui.date_to_button.set_active)
            self._reset_calendar_window(button)
            if button.get_active():
                self.calendar_window_controller.show(button)

    def on_use_date_checkbox_toggled(self, checkbox):
        """Handler for checkbox use date interval.
        'checkbox' is the 'Use date interval' checkbox control."""
        use_date_interval = checkbox.get_active()
        self.gui.date_from_button.set_sensitive(use_date_interval)
        self.gui.date_to_button.set_sensitive(use_date_interval)

    def _load_app_settings(self):
        """ Load application settings from home directory. """
        data = appsettings.load_app_settings()
        account_info, deletion_filters, storing_filters = data

        if account_info:
            server_info, user_info = account_info
        else:
            server_info = '', 0, '110'
            user_info = '', ''

        host, connection_type, port = server_info
        user, pwd = user_info
        self.gui.host_entry.set_text(host)
        self.gui.user_entry.set_text(user)
        self.gui.password_entry.set_text(pwd)
        self.gui.port_entry.set_text(port)
        self.on_account_entry_changed(None)
        self.gui.connection_combo.set_active(connection_type)
        if deletion_filters:
            model = AppRegistry.get_instance().get_deletion_filters()
            model.load_storage(deletion_filters)
        if storing_filters:
            model = AppRegistry.get_instance().get_storing_filters()
            model.load_storage(storing_filters)

    @staticmethod
    def _get_date_label(date):
        """Get label for required date.
        'date' is the required date."""
        label = _('Not defined')
        if date:
            label = date.strftime('%x')
        return label

    def _update_datetime_from(self, date):
        """Update Date Since button text.
        'date' is the new shown date."""
        self.date_from = date
        self.gui.date_from_button.set_label(self._get_date_label(date))

    def _update_datetime_to(self, date):
        """Update Date To button text.
        'date' is the new shown date."""
        self.date_to = date
        self.gui.date_to_button.set_label(self._get_date_label(date))

    def _show_del_confirmation(self, _delete, _total):
        """Show delete messages confirmation.
        'delete_count' is the amount of deleted messages.
        'total_count' is the total amount of messages."""
        msg = gtk.MessageDialog(self.gui.main_window, gtk.DIALOG_MODAL,
                                gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
            _('You proceed to delete %(_delete)d messages '
              'from %(_total)d total. Are you sure?') % locals())
        result = (msg.run() == gtk.RESPONSE_YES)
        msg.destroy()
        return result

    @idlefunction
    def _show_connection_error(self, exception):
        """ Show connection error.
        'exception' is the exception information."""
        msg_strings = []
        msg_strings.append(_('An error occurred during server connection. '
                        'Please check connection settings.'))
        msg_strings.append('\n\n')
        msg_strings.append(_('Error details: %s') % exception)
        msg = gtk.MessageDialog(self.gui.main_window, gtk.DIALOG_MODAL,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                        ''.join(msg_strings))
        msg.run()
        msg.destroy()

    def _show_error(self, exception, message):
        """Show error.
        'exception' is the exception information.
        'message' is the corresponding message."""
        print_exception(exception, message)
        self._show_connection_error(exception)

    def _show_message(self, msg):
        """Show downloaded message.
        'msg' is the downloaded message."""
        window = gtk.Dialog(None, self.gui.main_window, 0,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        scroll_window = gtk.ScrolledWindow()
        scroll_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        text_buffer = gtk.TextBuffer(None)
        textview = gtk.TextView(text_buffer)
        text_buffer.set_text(msg)
        scroll_window.add(textview)
        scroll_window.show()
        textview.show()
        vbox = window.__getattribute__('vbox')
        vbox.pack_start(scroll_window, True, True, 0)
        window.resize(640, 480)
        window.run()
        window.destroy()

    def _setup_filters(self):
        """ Setup filters. """
        deletion_filters_view = FilterView()
        deletion_filters = AppRegistry.get_instance().get_deletion_filters()
        deletion_filters_view.make_view(deletion_filters.tree_store,
            self.gui.deletion_filters_view)

        storing_filters_view = FilterView()
        storing_filters = AppRegistry.get_instance().get_storing_filters()
        storing_filters_view.make_view(storing_filters.tree_store,
           self.gui.storing_filters_view)

        storing_filters.update_func = self._update_filter
        deletion_filters.update_func = self._update_filter
        self._update_filter()

    def _apply_filter(self, filter_model, is_delete):
        """Apply filter for headers.
        'filter_model' is the model of the filter.
        'is_delete' is the flag of type of the filter."""
        headers_model = AppRegistry.get_instance().get_headers_model()
        headers_model.apply_filter(filter_model, is_delete)
        self.update_status()

    def _update_filter(self):
        """ Update filters buttons. """
        del_filter_mdl = AppRegistry.get_instance().get_deletion_filters()
        del_filters_count = len(del_filter_mdl.tree_store)

        store_filter_mdl = AppRegistry.get_instance().get_storing_filters()
        storing_filters_count = len(store_filter_mdl.tree_store)

        self.gui.apply_deletion_filters_button.set_sensitive(
                                                    del_filters_count > 0)

        is_del_filter_selected = bool(del_filters_count > 0 \
            and del_filter_mdl.current_path)
        self.gui.delete_deletion_filter_button.set_sensitive(
                                                    is_del_filter_selected)
        self.gui.edit_deletion_filter_button.set_sensitive(
                                                    is_del_filter_selected)

        self.gui.apply_storing_filters_button.set_sensitive(
                                                    storing_filters_count > 0)

        is_store_filter_selected = bool(storing_filters_count > 0 \
            and store_filter_mdl.current_path)
        self.gui.delete_storing_filter_button.set_sensitive(
                                                    is_store_filter_selected)
        self.gui.edit_storing_filter_button.set_sensitive(
                                                    is_store_filter_selected)

    def update_status(self):
        """ Update status bar with information about deleted messages. """
        headers_model = AppRegistry.get_instance().get_headers_model()
        deleted, hidden, total = headers_model.get_msg_counters()
        self.gui.statusbar.push(1, 
            _('Messages: %(total)d total, %(hidden)d hidden, %(deleted)d'
              ' for deletion') % locals())
        self.gui.clear_all_button.set_sensitive(deleted > 0)
        self.gui.select_all_button.set_sensitive(deleted != total - hidden)
        self.gui.preview_button.set_sensitive(False)

    def _update_text_field(self, combo, tree):
        """Update text field from current values of headers and filters.
        'combo' is the 'Filter Type' combobox.
        'tree' is the headers tree."""
        path = tree.get_cursor()[0]
        filter_field = combo.get_active()
        if path and filter_field != -1:
            headers_model = AppRegistry.get_instance().get_headers_model()
            mdl = headers_model.tree_model
            msg_iter = mdl.get_iter(path)
            value =  mdl.get_value(msg_iter, filter_field + 1)
            self.gui.filter_text_entry.set_text(value)

    @idlefunction
    def _stop_downloading(self):
        """ Stop downloading email headers. """
        headers_model = AppRegistry.get_instance().get_headers_model()
        headers_model.is_download_stopped = True
        self._is_downloading_headers = False
        self.gui.refresh_button.set_label('gtk-refresh')
        self._apply_all_filters()
        self.update_status()
        return True

    @idlefunction
    def _set_progressbar_idle(self):
        """ Set progressbar idle text. """
        self.gui.progressbar.set_text(_('Idle'))
        self.gui.progressbar.set_fraction(0)

    @idlefunction
    def _set_progressbar_fraction(self, fraction):
        """Set progressbar fraction.
        'fraction' is the new fraction value for progress bar."""
        self.gui.progressbar.set_fraction(fraction)

    @idlefunction
    def _set_progressbar_text(self, text):
        """Set progressbar text.
        'text' is the new text for progress bar."""
        self.gui.progressbar.set_text(text)

    def _download_headers(self):
        """ Download email headers. """
        self._is_downloading_headers = True
        headers_model = AppRegistry.get_instance().get_headers_model()
        headers_model.is_download_stopped = False
        callbacks = self._set_progressbar_text, self._set_progressbar_idle, \
            self._set_progressbar_fraction, self._stop_downloading, \
            self._show_error
        time_period = self.gui.use_date_interval_checkbox.get_active(), \
            self.date_from, self.date_to
        headers_model.download_headers(self._get_account_info(), time_period,
                                    callbacks)
        return True

    def _refresh_messages(self):
        """ Delete email messages. """
        self.gui.refresh_button.set_label('gtk-stop')
        headers_model = AppRegistry.get_instance().get_headers_model()
        headers_model.is_deletion_stopped = False
        if headers_model.check_for_assurance(self._show_del_confirmation):
            callbacks = self._set_progressbar_text, \
                self._set_progressbar_idle, self._set_progressbar_fraction, \
                self._stop_refreshing, self._show_error
            headers_model.delete_msgs(self._get_account_info(), callbacks)
        else:
            self._stop_refreshing(False)

    def _get_account_info(self):
        """ Get account information. """
        connection_type = self.gui.connection_combo.get_active()
        server_info = (self.gui.host_entry.get_text(), connection_type,
                self.gui.port_entry.get_text())
        user_info = (self.gui.user_entry.get_text(),
                     self.gui.password_entry.get_text())
        return (server_info, user_info)

    def _apply_all_filters(self):
        """ Apply all filters. """
        self._apply_filter(
                    AppRegistry.get_instance().get_deletion_filters(), True)
        self._apply_filter(
                    AppRegistry.get_instance().get_storing_filters(), False)

    def _stop_refreshing(self, proceed_further):
        """Stop deleting email messages.
        'proceed_further' is the flag do we have to refresh messages further."""
        headers_model = AppRegistry.get_instance().get_headers_model()
        headers_model.is_deletion_stopped = True
        if proceed_further :
            self._download_headers()
        else :
            self._stop_downloading()



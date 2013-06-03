#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# * This Program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU Lesser General Public
# * License as published by the Free Software Foundation; either
# * version 2.1 of the License, or (at your option) any later version.
# *
# * Libav is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# * Lesser General Public License for more details.
# *
# * You should have received a copy of the GNU Lesser General Public
# * License along with Libav; if not, write to the Free Software
# * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Gst-gengui: event messages

based on list_store.py example from pygtk2

Copyright 2009, Florent Thiery, under the terms of LGPL
Copyright 2013, Dirk Van Haerenborgh, under the terms of LGPL

"""
__author__ = ("Florent Thiery <fthiery@gmail.com>", "Dirk Van Haerenborgh <vhdirk@gmail.com>")



from gi.repository import GLib, GObject, Gst, Gio, Gtk

try:
    import easyevent
except Exception:
    import event as easyevent

(
    COLUMN_SOURCE,
    COLUMN_NAME,
    COLUMN_DATA,
) = range(3)

class MessagesDisplayer(easyevent.User, Gtk.Window):
    def __init__(self, parent=None, pipelinemanager_instance=None):
        easyevent.User.__init__(self)
        self.register_event('gst_element_message')

        self.pipelinemanager_instance = pipelinemanager_instance

        Gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            #self.connect('destroy', lambda *w: gtk.main_quit())
            pass
        if pipelinemanager_instance is not None:
            title = pipelinemanager_instance.pipeline.get_name()
        else:
            title = self.__class__.__name__
        self.set_title(title)

        self.set_border_width(8)
        self.set_default_size(500, 250)

        vbox = Gtk.VBox(False, 8)
        self.add(vbox)

        label = Gtk.Label('This are the gst.Element originating messages')
        vbox.pack_start(label, False, False, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(sw, True, True, 0)

        # create tree model
        self.store = model = self.__create_model()

        # create tree view
        treeview = Gtk.TreeView(model)
        treeview.set_rules_hint(True)
        treeview.set_search_column(COLUMN_DATA)

        sw.add(treeview)

        # add columns to the tree view
        self.__add_columns(treeview)

        self.show_all()

    def evt_gst_element_message(self, event):
        if self.pipelinemanager_instance is not None:
            if not event.source.pipeline.get_name() == self.pipelinemanager_instance.pipeline.get_name():
                return
        data = event.content
        message_data = data['data']
        
        data_string = ''
        for i in range(message_data.n_fields()):
            key = message_data.nth_field_name(i)
            data_string = '{0} {1}:{2}'.format(data_string, key, message_data.get_value(key))
        self.append_data((data['source'], data['name'], data_string))

    def __create_model(self):
        lstore = Gtk.ListStore(
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING)
        return lstore

    def append_data(self, data):
        iter = self.store.append()
        self.store.set(iter,
                COLUMN_SOURCE, data[COLUMN_SOURCE],
                COLUMN_NAME, data[COLUMN_NAME],
                COLUMN_DATA, data[COLUMN_DATA],
        )

    def __add_columns(self, treeview):
        # column for source
        column = Gtk.TreeViewColumn('Source Element', Gtk.CellRendererText(),
                                     text=COLUMN_SOURCE)
        column.set_sort_column_id(COLUMN_SOURCE)
        treeview.append_column(column)

        # column for name
        column = Gtk.TreeViewColumn('Message Name', Gtk.CellRendererText(),
                                     text=COLUMN_NAME)
        column.set_sort_column_id(COLUMN_NAME)
        treeview.append_column(column)

        # column for data
        column = Gtk.TreeViewColumn('Message Data', Gtk.CellRendererText(),
                                     text=COLUMN_DATA)
        column.set_sort_column_id(COLUMN_DATA)
        treeview.append_column(column)

def main():
    MessagesDisplayer()
    Gtk.main()

if __name__ == '__main__':
    main()

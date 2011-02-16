#!/usr/bin/env python
# based on list_store.py example from pygtk2

import gobject
import gtk
try:
    import easyevent
except Exception:
    import event as easyevent

(
    COLUMN_SOURCE,
    COLUMN_NAME,
    COLUMN_DATA,
) = range(3)

class MessagesDisplayer(easyevent.User, gtk.Window):
    def __init__(self, parent=None, pipelinemanager_instance=None):
        easyevent.User.__init__(self)
        self.register_event('gst_element_message')

        self.pipelinemanager_instance = pipelinemanager_instance

        gtk.Window.__init__(self)
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

        vbox = gtk.VBox(False, 8)
        self.add(vbox)

        label = gtk.Label('This are the gst.Element originating messages')
        vbox.pack_start(label, False, False)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)

        # create tree model
        self.store = model = self.__create_model()

        # create tree view
        treeview = gtk.TreeView(model)
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
        keys = message_data.keys()
        data_string = ''
        for key in keys:
            data_string = '%s %s:%s' %(data_string, key, message_data[key])
        self.append_data((data['source'], data['name'], data_string))

    def __create_model(self):
        lstore = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING)
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
        column = gtk.TreeViewColumn('Source Element', gtk.CellRendererText(),
                                     text=COLUMN_SOURCE)
        column.set_sort_column_id(COLUMN_SOURCE)
        treeview.append_column(column)

        # column for name
        column = gtk.TreeViewColumn('Message Name', gtk.CellRendererText(),
                                     text=COLUMN_NAME)
        column.set_sort_column_id(COLUMN_NAME)
        treeview.append_column(column)

        # column for data
        column = gtk.TreeViewColumn('Message Data', gtk.CellRendererText(),
                                     text=COLUMN_DATA)
        column.set_sort_column_id(COLUMN_DATA)
        treeview.append_column(column)

def main():
    MessagesDisplayer()
    gtk.main()

if __name__ == '__main__':
    main()

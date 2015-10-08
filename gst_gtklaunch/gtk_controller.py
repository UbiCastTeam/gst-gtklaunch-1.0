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
Gst-gengui: Gtk UI builder

Copyright 2009, Florent Thiery, under the terms of LGPL
Copyright 2013, Dirk Van Haerenborgh, under the terms of LGPL

"""
__author__ = ("Florent Thiery <fthiery@gmail.com>", "Dirk Van Haerenborgh <vhdirk@gmail.com>")

import os
import time
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, GObject, Gst, Gio, Gtk
from gi.repository import Gdk, GdkX11, GstVideo

import logging
logger = logging.getLogger('gst-gtklaunch-gtk')

from .gstintrospector import PipelineIntrospector
from .util import get_hms_string_from_seconds

class VideoWidget(Gtk.DrawingArea):
    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.imagesink = None
        self.set_double_buffered(False)
        #self.unset_flags(Gtk.DOUBLE_BUFFERED)

    def do_expose_event(self, event):
        if self.imagesink:
            self.imagesink.expose()
            return False
        else:
            return True

    def set_sink(self, sink):
        win = self.get_property('window')
        if win:
            xid = win.get_xid()
            assert xid
            self.imagesink = sink
            self.imagesink.set_window_handle(xid)

    def get_sink(self):
        return self.imagesink

class GtkGstController(object):

    def delete_event(self, widget, event, data=None):
        logger.info("delete event occurred")
        self.pipeline_launcher.stop()
        return False

    def destroy(self, widget, data=None):
        logger.info("destroy signal occurred")
        Gtk.main_quit()

    def __init__(self, pipeline_launcher, show_messages=False, display_preview=True, ignore_list=[]):
        self.videowidget = None
        self.folder = None
        self.props_visible = False
        self.prop_watchlist = list()

        self.pipeline_launcher = pipeline_launcher
        self.ignore_list = ignore_list
        
        self.prop_list = list()
        
        if show_messages:
            self._on_show_messages()

        self.pipeline_launcher.bus.enable_sync_message_emission()
        self.pipeline_launcher.bus.connect('sync-message::element', self.on_sync_message)
        self.pipeline_launcher.bus.connect('message::state-changed', self.on_state_change_message)

        self.poll_id = None

        self.window = w = Gtk.Window()
        w.set_title("gst-gtklaunch-1.0")
        w.set_size_request(800, 600)
        w.set_border_width(6)

        self.main_container = Gtk.VBox(False, 0)
        self.window.add(self.main_container)

        self.preview_and_control = Gtk.HBox(False, 0)

        self.resizable_container = Gtk.HPaned()
        self.resizable_container.set_wide_handle(True)

        self.preview_and_control.pack_start(self.resizable_container, True, True, 0)
        self.show_props_btn = show_props_btn = self._create_button("<", callback=self.toggle_show_props)
        self.preview_and_control.pack_end(show_props_btn, False, False, 0)

        self.properties_container = Gtk.VBox(False, 0)

        # video sink area
        self.preview_container = Gtk.HBox(False, 0)
        self.preview_container.set_size_request(320, 240)

        # properties area
        self.scrolled_window = scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(0)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        scrolled_window.add_with_viewport(self.properties_container)
        scrolled_window.set_size_request(400,200)

        # play/stop/pause controls
        pipeline_controls = self._create_pipeline_controls(pipeline_launcher)

        if display_preview:
            self.resizable_container.pack1(self.preview_container, resize=True, shrink=True)

        self.main_container.pack_start(self.preview_and_control, True, True, 0)
        self.main_container.pack_end(pipeline_controls, False, False, 0)

        self.window.show_all()

    def toggle_show_props(self, *args):
        self.set_properties_pane_visible(not self.props_visible)

    def set_properties_pane_visible(self, state):
        if state:
            self.resizable_container.pack2(self.scrolled_window, resize=True, shrink=True)
            self.props_visible = True
            self.scrolled_window.show()
            self.properties_container.show()
            self.show_props_btn.set_label('>')
        else:
            self.resizable_container.remove(self.scrolled_window)
            self.props_visible = False
            self.show_props_btn.set_label('<')

    def on_sync_message(self, bus, message):
        if message.get_structure() is None:
            return
        if message.get_structure().get_name() == 'prepare-window-handle':
            logger.debug("prepare-window-handle, {0}".format(message))
            self._create_videowidget(message)
            
    def on_state_change_message(self, bus, message):
        for prop, widget in self.prop_list:
            GObject.idle_add(self.update_widget_value, widget, prop)
        

    def _create_videowidget(self, message):
        self.videowidget = None
        self.videowidget = videowidget = VideoWidget()
        videowidget.show()
        self.preview_container.pack_start(videowidget, True, True, 0)
        # Sync with the X server before giving the X-id to the sink
        GObject.idle_add(Gdk.Display.get_default().sync, priority=GObject.PRIORITY_HIGH)
        GObject.idle_add(videowidget.set_sink, message.src, priority=GObject.PRIORITY_HIGH)
        message.src.set_property('force-aspect-ratio', True)

    def _create_pipeline_controls(self, pipeline_launcher):
        container = Gtk.VBox(False,3)

        label = Gtk.Label("Pipeline description")
        entry = Gtk.TextView()
        entry.set_size_request(400,50)
        entry.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textbuffer = textbuffer = entry.get_buffer()
        textbuffer.set_text(pipeline_launcher.pipeline_desc)
        textbuffer.set_modified(False)

        container.add(label)
        container.add(entry)

        container_btns = Gtk.HBox()
        container.add(container_btns)

        self.refresh_button = refresh_btn = self._create_button(label="Refresh", callback=self._refresh, container=container_btns)
        refresh_btn.set_sensitive(False)

        self.state_label = self._create_label("State", container=container_btns)
        self.position_label = self._create_label("Position", container=container_btns)
        self._create_button(label="Play", callback=self.run_pipeline, container=container_btns)
        self._create_button(label="Stop", callback=self.stop_pipeline, container=container_btns)
        self._create_button(label="Pause", callback=pipeline_launcher.pause, container=container_btns)
        self._create_button(label="Send EOS", callback=pipeline_launcher.send_eos, container=container_btns)
        self._create_button(label="Show tree", callback=self._on_show_tree, container=container_btns)
        self._create_button(label="Show messages", callback=self._on_show_messages, container=container_btns)
        if "dumpsink" in pipeline_launcher.pipeline_desc:
            logger.info('Found dumpsink in pipeline, adding take picture button')

            picture_btns = Gtk.HBox(homogeneous=False)
            container.add(picture_btns)

            self.take_picture_btn = take_picture_btn = self._create_button(label="Take picture", callback=self._on_take_picture, container=picture_btns)
            take_picture_btn.set_sensitive(False)
            self.folder_btn = self._create_button(label="Choose folder", callback=self._on_choose_folder, container=picture_btns)

            label = Gtk.Label("Filename:")
            self.filename_entry = entry = Gtk.TextView()
            entry.set_editable(False)
            entry.set_size_request(100, -1)
            self.pic_textbuffer = pic_textbuffer = entry.get_buffer()
            fname = "%s.jpg" %int(time.time())
            pic_textbuffer.set_text(fname)
            pic_textbuffer.set_modified(False)
            picture_btns.add(label)
            picture_btns.add(entry)
        return container

    def run_pipeline(self, *args):
        self.pipeline_launcher.run()
        self._start_pollings()
        #TODO: update controls

    def gtk_main(self):
        self.main()
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        GObject.idle_add(self.run_pipeline)
        Gtk.main()

    def main(self):
        self._build_elements()
        GObject.timeout_add(500, self._check_for_pipeline_changes)

    def stop_pipeline(self, *args):
        self.pipeline_launcher.stop(*args)
        self._stop_pollings()
        self._clean_previews()
        self._reset_controls()

    def _reset_controls(self):
        self.position_label.set_text("")

    def _build_elements(self):
        introspector = PipelineIntrospector(self.pipeline_launcher.pipeline, self.ignore_list)
        for element in introspector.elements:
            self.add_element_widget(element)
            if element.implements_childproxy:
                for elem in element.children:
                    self.add_element_widget(elem, element.name)
                element.connect_child_added(self.add_element_widget)
                element.connect_child_removed(self.remove_element_widget)

    def _start_pollings(self):
        if not self.poll_id:
            self.poll_id = GObject.timeout_add(500, self._do_checks)

    def _stop_pollings(self):
        if self.poll_id:
            GObject.source_remove(self.poll_id)
            self.poll_id = None

    def _do_checks(self):
        self._check_for_pipeline_position()
        self._check_for_pipeline_state()
        self._poll_properties_watchlist()
        return True

    def _on_show_messages(self, *args):
        from .messages import MessagesDisplayer
        test  = MessagesDisplayer(pipelinemanager_instance=self.pipeline_launcher)

    def yesno(self, label):
        d = Gtk.MessageDialog(
            parent=self.window,
            type=Gtk.MessageType.QUESTION,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_YES, Gtk.ResponseType.OK),
            message_format=label,
        )
        r = d.run()
        d.destroy()
        return r == Gtk.ResponseType.OK

    def _on_take_picture(self, *args):
        sink = self.pipeline_launcher.pipeline.get_by_name('dumpsink')
        if sink:
            sample = sink.get_property('last-sample')
            buf = sample.get_buffer()
            diff = (buf.pts/Gst.SECOND - self.position)
            if abs(diff) > 1:
                logger.warning('Timestamp between pipeline position and dump differ by more than 1 second, you may be capturing a late buffer')
            cap = sample.get_caps()
            data = buf.extract_dup(0, buf.get_size())
            logger.info("Got picture: %s" %cap)
            if self.pic_textbuffer.get_modified():
                s, e = self.pic_textbuffer.get_bounds()
                fname = self.pic_textbuffer.get_text(s, e, include_hidden_chars=True)
            else:
                fname = "%s.jpg" %int(time.time())
                self.pic_textbuffer.set_text(fname)
                self.pic_textbuffer.set_modified(False)
            abs_fname = os.path.join(self.folder, fname)
            if os.path.isfile(abs_fname):
                overwrite = self.yesno("Are you sure you want to overwrite file %s ?" %abs_fname)
                if not overwrite:
                    return
            f = open(abs_fname, "wb")
            f.write(data)
            f.close()
            logger.info('Wrote file %s (%i kbytes)' %(abs_fname, round(buf.get_size()/1024)))
            size = int(round(os.path.getsize(abs_fname)/1024))
            self.take_picture_btn.set_label('Picture saved (%s kB)' %size)
            GObject.timeout_add_seconds(3, self._reset_take_picture_btn)
        else:
            logger.error('dumpsink element not found')

    def _reset_take_picture_btn(self):
        self.take_picture_btn.set_label('Take picture')

    def _on_choose_folder(self, *args):
        folderchooser = Gtk.FileChooserDialog(
            title="Choose folder to store pictures", 
            parent=self.window, 
            action=Gtk.FileChooserAction.SELECT_FOLDER, 
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE, Gtk.ResponseType.OK),
        )
        response = folderchooser.run()
        if response == Gtk.ResponseType.OK:
            folder = folderchooser.get_filename()
            if os.path.isdir(folder):
                logger.info('Chose folder %s' %folder)
                self.folder = folder
                self.folder_btn.set_label('Folder: %s' %folder)
                self.take_picture_btn.set_sensitive(True)
                self.filename_entry.set_editable(True)
        folderchooser.destroy()

    def _on_show_tree(self, *args):
        dotfile = self.pipeline_launcher.dump_dot_file()
        if dotfile:
            os.system('xdot %s' %dotfile)

    def _clean_previews(self):
        for video in self.preview_container:
            self.preview_container.remove(video)
            del(video)

    def _check_for_pipeline_state(self):
        state = self.pipeline_launcher.get_state()
        self.state_label.set_text(state)

    def _check_for_pipeline_position(self):
        self.position = position = self.pipeline_launcher.get_position()
        if self.pipeline_launcher.has_duration():
            duration = self.pipeline_launcher.get_duration()
            self.position_label.set_text("Position: %s / %s" %(get_hms_string_from_seconds(position), get_hms_string_from_seconds(duration)))
        else:
            self.position_label.set_text("Live since %s" %get_hms_string_from_seconds(position))

    def _check_for_pipeline_changes(self):
        if self.textbuffer.get_modified():
            self.new_description = self.textbuffer.get_text(*self.textbuffer.get_bounds(), include_hidden_chars=False)
            self.refresh_button.set_sensitive(True)
        return True

    def _reset_property(self, widget, args):
        logger.debug("Resetting property value to default value")
        prop = args[0]
        adj = args[1]
        prop.parent_element.set_property(prop.name, prop.default_value)
        prop.update_value()
        adj.set_value(prop.value)

    def _refresh(self, *args):
        self._clean_controls()
        self.stop_pipeline()
        logger.info("Refreshing pipeline with description: {0}" .format(self.new_description))
        self.pipeline_launcher.redefine_pipeline(new_string=self.new_description)
        self.pipeline_launcher.bus.connect('message::element', self.on_sync_message)
        self.run_pipeline()
        self.textbuffer.set_modified(False)
        self._build_elements()

    def _clean_controls(self):
        logger.debug("Removing all controls")
        for item in self.properties_container:
            self.properties_container.remove(item)

    def _create_label(self, label="Hello", container=None):
        label = Gtk.Label.new(label)
        if container is not None:
           container.add(label)
        return label

    def _create_button(self, label="Hello", callback=None, callback_args=None, container=None):
        button = Gtk.Button(label)
        button.show()
        if container is not None:
            container.add(button)
        if callback is not None:
            button.connect("clicked", callback, callback_args)
        return button

    def _create_element_widget(self, element):
        mcontainer = Gtk.Expander.new(element.name) 
        container = Gtk.VBox()
        mcontainer.add(container)
        logger.debug("Element name: {0}".format(element.name))
        if len(element.number_properties) > 0:
            for number_property in element.number_properties:
                spinner = self._create_spinner(number_property)
                container.pack_start(spinner, False, False, 6)
        if len(element.boolean_properties) > 0:
            for boolean_property in element.boolean_properties:
                check_btn = self._create_check_btn(boolean_property)
                container.pack_start(check_btn, False, False, 6)
        if len(element.string_properties) > 0:
            for string_property in element.string_properties:
                if string_property.name == "location":
                    entry = self._create_filebrowser(string_property)
                else:
                    entry = self._create_entry(string_property)
                container.pack_start(entry, False, False, 6)
        if len(element.enum_properties) > 0:
            for enum_property in element.enum_properties:
                enum = self._create_enum_combobox(enum_property)
                container.pack_start(enum, False, False, 6)
        container.show()
        mcontainer.show()
        return mcontainer


    # FIXME: notify:: should to this !
    def _poll_properties_watchlist(self):
        # polling is called by _do_checks
        for prop in self.prop_watchlist:
            value = prop['elt'].get_property(prop['prop_name'])
            if value != prop['last_seen']:
                prop['cb'](value)
        return True

    def notify_property(self, element, prop_name, callback):
        self.prop_watchlist.append({'elt': element, 'prop_name': prop_name, 'cb': callback, 'last_seen': element.get_property(prop_name)})
        
    
        
    ################################################

    def _create_spinner(self, prop):
        if prop.is_int:
            step_incr=1
            num_digits = 0
        else:
            step_incr=0.1
            num_digits=1

        adj = Gtk.Adjustment(value=prop.value, lower=prop.minimum, upper=prop.maximum, step_incr=step_incr, page_incr=0, page_size=0)

        container = Gtk.HBox()
        label = Gtk.Label(prop.human_name)
        spinner = Gtk.SpinButton.new(adj, 0.1, num_digits)

        slider = Gtk.HScale.new(adj)
        # showing the value uses space, its shown in the entry next to it anyway
        slider.set_draw_value(False)
        #slider.set_digits(num_digits)
        #slider.set_size_request(300, 20)
        slider.show()

        reset_btn = self._create_button("Reset", callback=self._reset_property, callback_args=[prop, adj])

        container.pack_start(label, False, True, 20)
        container.pack_end(reset_btn, False, True, 20)
        container.pack_end(spinner, False, True, 20)
        container.pack_end(slider, True, True, 20)

        if not prop.is_readonly:
            adj.connect("value_changed", self.apply_changes, prop)
            
        else:
            container.set_sensitive(False)
            Gst_elt = prop.parent_element._Gst_element
            # FIXME: why doesn't it work ?
            #Gst_elt.connect('notify::{0}'.format(prop.name), adj.set_value)
            self.notify_property(Gst_elt, prop.name, adj.set_value)

        self.prop_list.append((prop, adj))
        label.show()
        spinner.show()
        container.show()

        return container

    def _create_check_btn(self, prop):
        button = Gtk.CheckButton(prop.human_name)
        button.set_active(prop.value)
        if not prop.is_readonly:
            button.connect("toggled", self.apply_changes, prop)
        else:
            button.set_sensitive(False)
        button.show()
        self.prop_list.append((prop, button))
        return button

    def _create_enum_combobox(self, prop):
        container = Gtk.HBox()
        label = Gtk.Label(prop.human_name)
        label.show()
        combobox = Gtk.ComboBoxText.new()
        for value in prop.values_list:
            combobox.append_text(value)
        combobox.set_active(prop.value)
        combobox.connect("changed", self.apply_changes, prop)
        combobox.show()
        container.pack_start(label, False, True, 20)
        container.pack_end(combobox, True, True, 20)
        container.show()
        self.prop_list.append((prop, combobox))
        return container

    def _create_entry(self, prop):
        logger.debug("Creating entry for property {0}".format(prop.name))
        container = Gtk.HBox()
        label = Gtk.Label(prop.human_name)
        label.show()
        entry = Gtk.Entry()
        entry.set_text(prop.value)

        if not prop.is_readonly:
            entry.connect("activate", self.apply_changes, prop)
        else:
            entry.set_sensitive(False)
        entry.show()
        container.pack_start(label, False, True, 20)
        container.pack_end(entry, True, True, 20)
        container.show()
        self.prop_list.append((prop, entry))
        return container

    def _create_filebrowser(self, prop):
        container = Gtk.HBox()
        container.show()

        label = Gtk.Label(prop.name)
        label.show()
        container.add(label)

        open_btn = Gtk.FileChooserButton('Select a file')
        open_btn.connect('file-set', self._on_file_set, prop)
        open_btn.show()
        container.add(open_btn)

        self.prop_list.append((prop, open_btn))

        return container

    def _on_file_set(self, source, prop):
        fname = source.get_filename()
        if prop.parent_element.name == 'filesrc':
            #FIXME
            logger.info('Changing location on filesrc (to %s) is not supported, restarting pipeline' %fname)
            #prop.parent_element._Gst_element.set_property("location", fname)
            #self.pipeline_launcher.stop()
            #self.apply_changes(source, prop)
            #self.pipeline_launcher.run()
            #self.stop_pipeline()
            self.pipeline_launcher.redefine_pipeline()
            #self._clean_controls()
            self.pipeline_launcher.bus.connect('message::element', self.on_sync_message)
            #self._build_elements()
            prop.parent_element._Gst_element.set_property(prop.name, fname) 
            self.pipeline_launcher.run()
        else:
            self.apply_changes(source, prop)

    def add_controller(self, widget, parent_name=None):
        if parent_name:
            children = self.properties_container.get_children()
            for child in children:
                if child.get_label() == parent_name:
                    child.get_child().add(widget)
        else:
            self.properties_container.pack_start(widget, False, False, 5)

    def add_element_widget(self, element, parent_name=None):
        logger.debug("Adding widgets for element {0}".format(element.name))
        widget = self._create_element_widget(element)
        self.add_controller(widget, parent_name)
        
    def remove_element_widget(self, element, parent_name=None):
        logger.debug("Removing widgets for element {0}".format(element.name))
        children = self.properties_container.get_children()
        if parent_name:
            for child in children:
                if child.get_label() == parent_name:
                    pchild = child.get_child()
                    for cchild in pchild.get_children():
                        if hasattr(cchild, 'get_label'):
                            if cchild.get_label() == element.name:
                                pchild.remove(cchild)
        for child in children:
            if child.get_name() == element.name:
                children.remove(child)



    def _get_value_by_class(self, widget, prop):
        if isinstance(widget, Gtk.CheckButton):
            value = widget.get_active()
        elif isinstance(widget, Gtk.Adjustment):
            value = widget.get_value()
            if prop.is_int:
                value = int(value)
        elif isinstance(widget, Gtk.ComboBox):
            value = widget.get_active()
        elif isinstance(widget, Gtk.Entry):
            value = widget.get_text()
        elif isinstance(widget, Gtk.FileChooserButton):
            value = widget.get_filename()
        else:
            logger.error('Cannot get value of widget of class {0} for property {1}'.format(widget.__class__, prop.name))
        return value
        
    def _set_value_by_class(self, widget, prop):
        if isinstance(widget, Gtk.CheckButton):
            widget.set_active(prop.value)
        elif isinstance(widget, Gtk.Adjustment):
            widget.set_value(prop.value)
        elif isinstance(widget, Gtk.ComboBox):
            widget.set_active(prop.value)
        elif isinstance(widget, Gtk.Entry):
            widget.set_text(prop.value)
        elif isinstance(widget, Gtk.FileChooserButton):
            widget.set_filename(prop.value)
        else:
            logger.error('Cannot set value of widget of class {0} for property {1}'.format(widget.__class__, prop.name))        
       
    def update_widget_value(self, widget, prop):
        prop.update_value()
        self._set_value_by_class(widget, prop)
       
    def apply_changes(self, widget, prop):
        value = self._get_value_by_class(widget, prop)
        logger.debug("Applying value {0} to property '{1}' of element {2}".format(value, prop.name, prop.parent_element.name))
        # FIXME: check MUTABLE property 
        if prop.name == "bitrate" and prop.parent_element.name == "theoraenc":
            self.stop()
        prop.parent_element.set_property(prop.name, value)
        if prop.name == "bitrate" and prop.parent_element.name == "theoraenc":
            self.pipeline_launcher.run()
        
        GObject.idle_add(self.update_widget_value, widget, prop)
        

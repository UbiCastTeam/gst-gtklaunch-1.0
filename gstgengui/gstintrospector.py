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
Gst-gengui: Gstreamer introspector

Scans pipelines for named elements and associated properties
When launched separately, prints all the found elements

Copyright 2009, Florent Thiery, under the terms of LGPL
Copyright 2013, Dirk Van Haerenborgh, under the terms of LGPL

"""
__author__ = ("Florent Thiery <fthiery@gmail.com>", "Dirk Van Haerenborgh <vhdirk@gmail.com>")

import logging
logger = logging.getLogger('Gst-gengui')

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, GObject, Gst, Gio, Gtk

IGNORE_LIST = []

NUMBER_GTYPES = (GObject.TYPE_INT, GObject.TYPE_UINT, GObject.TYPE_LONG, GObject.TYPE_ULONG, GObject.TYPE_INT64, GObject.TYPE_UINT64, GObject.TYPE_FLOAT, GObject.TYPE_DOUBLE)

INT_GTYPES = (GObject.TYPE_INT, GObject.TYPE_UINT, GObject.TYPE_LONG, GObject.TYPE_ULONG, GObject.TYPE_INT64, GObject.TYPE_UINT64)

STRING_GTYPES = (GObject.TYPE_CHAR, GObject.TYPE_UCHAR, GObject.TYPE_UNICHAR, GObject.TYPE_GSTRING, GObject.TYPE_STRING)

class Property(object):
    def __init__(self, property, parent_element):
        self.parent_element = parent_element
        self.description = property.blurb
        self.default_value = property.default_value
        self.name = property.name
        self.human_name = property.nick
        self.value_type = property.value_type
        self.is_readonly = (property.flags == 225)
        self.update_value()

    def update_value(self):
        value = self.parent_element._Gst_element.get_property(self.name)
        if value is None:
            if self.default_value is not None:
                value = self.default_value
            else:
                value = "Default"
        self.value = value

class BooleanProperty(Property):
    def __init__(self, property, parent_element):
        Property.__init__(self, property, parent_element)

class StringProperty(Property):
    def __init__(self, property, parent_element):
        Property.__init__(self, property, parent_element)

class NumberProperty(Property):
    def __init__(self, property, parent_element):
        Property.__init__(self, property, parent_element)
        self.minimum = property.minimum
        self.maximum = property.maximum       
        self.is_int = self.value_type in INT_GTYPES

class EnumProperty(Property):
    def __init__(self, property, parent_element):
        Property.__init__(self, property, parent_element)
        self.value_type = GObject.TYPE_ENUM
        self.values_list = []
        if property.__gtype__.has_value_table:
            values = property.enum_class.__enum_values__
            for index in values:
                self.values_list.append(values[index].value_name)
                # FIXME: find more proper way to do it (check buzztard)
                # Nb: l'index, value_name et value_nick peuvent tous deux etre utilisés pour set_property

class Element(object):
    def __init__(self, Gst_element, ignore_list=IGNORE_LIST):
        self._Gst_element = Gst_element
        _properties_list = GObject.list_properties(self._Gst_element)
        
        #print( Gst.Object.get_properties(self._Gst_element))
        
        self.implements_childproxy = GObject.type_from_name("GstChildProxy") in GObject.type_interfaces(self._Gst_element)
        
        if hasattr(self._Gst_element, "get_factory"):
            self.name = self._Gst_element.get_factory().get_name()
        else:
            self.name = self._Gst_element.get_name()

        self.number_properties = number_properties = []
        self.boolean_properties = boolean_properties = []
        self.string_properties = string_properties = []
        self.enum_properties = enum_properties = []

        for property in _properties_list:
            if property.name in ignore_list:
                logger.debug("Property {0} is in ignore list, skipping".format(property.name))

            elif property.value_type in NUMBER_GTYPES:
                number_property = NumberProperty(property, self)
                number_properties.append(number_property)

            elif property.value_type == GObject.TYPE_BOOLEAN:
                boolean_property = BooleanProperty(property, self)
                boolean_properties.append(boolean_property)

            elif property.value_type in STRING_GTYPES: 
                string_property = StringProperty(property, self)
                string_properties.append(string_property)
          
            elif property.value_type.is_a(GObject.TYPE_ENUM):
                enum_property = EnumProperty(property, self)
                enum_properties.append(enum_property)

            else:
                logger.error("Property '{0}' with type {1} has no associated known types, skipping".format(property.name, property.value_type))

    def set_property(self, property, value):
        self._Gst_element.set_property(property, value)
        
        
    def _child_changed(self, parent, child, name, callback):
        callback(Element(child), self.name)
        
    def connect_child_added(self, callback):
        self._Gst_element.connect("child-added", self._child_changed, callback)
        
    def connect_child_removed(self, callback):
        self._Gst_element.connect("child-removed", self._child_changed, callback)

class PipelineIntrospector(object):
    def __init__(self, pipeline, ignore_list):
        self.pipeline = pipeline
        self.ignore_list = ignore_list
        self.gst_elements = []
        self.elements = []
        self._get_Gst_elements()
        self._introspect_elements()

    def _get_Gst_elements(self):
        gstit = self.pipeline.iterate_elements()
        elt = gstit.next()
        while(elt[0] == Gst.IteratorResult.OK):
            self.gst_elements.insert(0, elt[1])
            elt = gstit.next()

    def _introspect_elements(self):
        for gst_element in self.gst_elements:
            element = Element(gst_element, self.ignore_list)
            self.elements.append(element)

    def print_all(self):
        print('Printing all of them')
        for element in self.elements:
            print(element)
            if True:
                print("\nElement: {0}".formmat(element.name))
                for property in element.number_properties:
                    print(property.name)

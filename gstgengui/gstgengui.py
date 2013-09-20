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
GstGengui: utility for testing and controlling live GStreamer pipelines and elements.

Copyright 2009, Florent Thiery, under the terms of LGPL
Copyright 2013, Dirk Van Haerenborgh, under the terms of LGPL

"""
__author__ = ("Florent Thiery <fthiery@gmail.com>", "Dirk Van Haerenborgh <vhdirk@gmail.com>")
__package__= 'gstgengui'


import os
os.environ['GI_TYPELIB_PATH'] = "/usr/local/lib/girepository-1.0:/usr/lib/girepository-1.0"

import sys
import logging
logger = logging.getLogger('gstgengui')

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk

from .gstmanager import PipelineManager
from .gtk_controller import GtkGstController


def init():
    try:
        assert os.environ.get('GST_DEBUG_DUMP_DOT_DIR', None)
    except (NameError, AssertionError):
        os.environ['GST_DEBUG_DUMP_DOT_DIR'] = os.getcwd()
        
    GObject.threads_init()
    Gst.init(None)
    Gst.debug_set_active(True)
    Gst.debug_set_colored(True)
    Gst.debug_set_default_threshold(Gst.DebugLevel.WARNING)


def parse_args(pipeline):
    desc = ""
    for arg in pipeline:
        desc += " "+arg
    logger.debug("gst-launch pipeline is: {0}".format(desc))
    #print("gst-launch pipeline is: {0}".format(desc))
    return desc


def main():

    import argparse
    parser = argparse.ArgumentParser(prog="gstgengui", description='utility for testing and controlling live GStreamer pipelines and elements',  formatter_class=argparse.ArgumentDefaultsHelpFormatter, conflict_handler='resolve')
    parser.add_argument('-v', "--verbose", action="store_true", dest="verbose", default=False, help="Use DEBUG verbosity level")
    parser.add_argument('-m', "--messages", action="store_true", dest="show_messages", default=False, help="Show gst.Element messages window before setting the pipeline to PLAYING")
    parser.add_argument('-c', "--config", dest="config", help="Loads the given configuration file")
    parser.add_argument('pipeline', nargs='*', help='Pipeline description')

    args = parser.parse_args()

    if args.verbose:
        verbosity = 'DEBUG'
    else:
        verbosity = 'INFO'


    logging.basicConfig(
        level=getattr(logging, verbosity),
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        stream=sys.stderr
    )
    
    #as defined in config.py
    configuration = {
        'name': None,
        'pipeline_desc': None,
        'ignore_list': ['parent'],
        'display_preview': True
    }

    if args.config:
        with open(args.config) as config:
            exec(config.read(), {}, configuration)
        

    if args.pipeline:
        configuration['pipeline_desc'] = parse_args(args.pipeline)


    if not configuration['pipeline_desc']:
        logger.error("Empty pipeline unauthorized, quitting")
        sys.exit(1)
        
    init()

    pipeline_launcher = PipelineManager(configuration['pipeline_desc'], configuration['name'])

    controller = GtkGstController(pipeline_launcher, args.show_messages, configuration['display_preview'], configuration['ignore_list'])

    controller.gtk_main()
    
if __name__ == '__main__':
    main()
    

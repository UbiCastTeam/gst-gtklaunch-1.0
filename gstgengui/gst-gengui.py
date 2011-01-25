#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2010, Florent Thiery, under the terms of LGPL
"""
import os
os.environ['GST_DEBUG_DUMP_DOT_DIR'] = '/tmp/'

import logging
logger = logging.getLogger('gst-gengui')

import gobject
gobject.threads_init()

if __name__ == '__main__':

    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] [pipeline description]")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Use DEBUG verbosity level")
    parser.add_option("-m", "--messages", action="store_true", dest="show_messages", default=False, help="Show gst.Element messages window before setting the pipeline to PLAYING")

    (options, args) = parser.parse_args()
    print options, args

    if options.verbose:
        verbosity = 'DEBUG'
    else:
        verbosity = 'INFO'

    import logging, sys

    logging.basicConfig(
        level=getattr(logging, verbosity),
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        stream=sys.stderr
    )

    def parse_args(args):
        desc = ""
        for arg in args:
            desc += " "+arg
        logger.debug("gst-launch pipeline is: %s" %desc)
        return desc 
 
    if len(args) == 0:
        logger.error("Empty pipeline unauthorized, quitting")
        sys.exit(1)
    else:
        string = parse_args(args)

    # We import it later on otherwise it messes up optparse
    from gstmanager import PipelineManager
    pipeline_launcher = PipelineManager(string)

    from gtk_controller import GtkGstController
    controller = GtkGstController(pipeline_launcher, options.show_messages)

    controller.main()

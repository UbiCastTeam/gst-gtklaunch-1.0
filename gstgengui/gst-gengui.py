#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2009, Florent Thiery, under the terms of LGPL
"""
import os
os.environ['GST_DEBUG_DUMP_DOT_DIR'] = '/tmp/'

import logging
logger = logging.getLogger('gst-gengui')

import gobject
gobject.threads_init()

from gstmanager import PipelineManager

if __name__ == '__main__':

    import logging, sys

    logging.basicConfig(
        level=getattr(logging, "DEBUG"),
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        stream=sys.stderr
    )

    def parse_argv(args):
        cmd = ""
        for n in range(1, len(args)):
            cmd+="%s " %args[n]
        logger.info("gst-launch pipeline is: %s" %cmd)
        return cmd
   
    from sys import argv
    if len(argv) <= 1:
        logger.info("No gst-launch syntax detected, using config file")
        import gstgengui.config
        string = gstgengui.config.pipeline_desc
    else:
        string = parse_argv (argv)
    pipeline_launcher = PipelineManager(string)

    from gtk_controller import GtkGstController
    controller = GtkGstController(pipeline_launcher)

    controller.main()

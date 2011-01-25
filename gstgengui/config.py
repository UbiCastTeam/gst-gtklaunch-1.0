#!/ur/bin/env python
# -*- coding: utf-8 -*-

"""
gst-gengui configuration: 
* define here your pipelines in the pipeline_desc string
* define the named elements you would like to scan for properties
* define the properties you would like to skip

Copyright 2009, Florent Thiery, under the terms of LGPL
"""

ignore_list = ["timestamp-offset","num-buffers", "display", "name", "external-opengl-context"]
pipeline_desc = "videotestsrc is-live=True ! video/x-raw-yuv, format=(fourcc)YUY2, width=(int)320, height=(int)240, framerate=(fraction)15/1 ! ffmpegcolorspace !  videobalance ! queue ! xvimagesink"

#pipeline_desc = "v4l2src ! queue ! videobalance name=image_settings ! queue ! tee name=tee ! queue ! ffmpegcolorspace ! queue ! xvimagesink sync=false tee. ! queue ! theoraenc name=encoder ! queue ! tee name=encoded_tee ! queue ! oggmux ! filesink name=filter location=/tmp/test.ogg encoded_tee. ! queue ! decodebin ! queue ! ffmpegcolorspace ! queue ! xvimagesink sync=false"

#pipeline_desc = "audiotestsrc name=src ! queue ! ladspa-alias name=filter ! queue ! ladspa-shaper name=filter2 ! queue ! audioconvert ! alsasink"

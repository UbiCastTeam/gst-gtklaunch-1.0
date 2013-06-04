#!/usr/bin/env python3
# -*- coding: utf-8 -*-



name = "test"
pipeline_desc = "videotestsrc ! video/x-raw, format=(string)YUY2, width=(int)320, height=(int)240, framerate=(fraction)15/1 ! videoconvert !  videobalance ! queue ! xvimagesink"

ignore_list = ['parent']

display_preview = True

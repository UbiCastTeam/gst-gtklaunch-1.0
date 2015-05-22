#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2015, Florent Thiery

def get_hms_string_from_seconds(seconds):
    text = "%02d:%02d:%02d" % get_hms_tuple_from_seconds(seconds)
    return text

def get_hms_tuple_from_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return hours, minutes, seconds

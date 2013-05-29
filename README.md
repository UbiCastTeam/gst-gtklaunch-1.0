# gst-gengui

gst-gengui is an utility for testing and controlling live GStreamer pipelines and elements.
It will inspect the specified pipeline to create the GTK GUI "automagically", based on the value type of properties.

gst-gengui currently requires (Ubuntu 13.04 package names):
   * python3-gi
   * gir1.2-gtk-3.0
   * gir1.2-gstreamer-1.0
   * graphviz 
   * xdot python interactive dot viewer (sudo easy_install xdot)

Non-packaged dependancies:
   * https://launchpad.net/easyevent
   * http://code.google.com/p/gstmanager/

It has been tested on Ubuntu 13.04

## Features

   * gst-launch-type syntax
   * pipeline controls: play, pause, stop, send_eos
   * pipeline states display: current state, current position, duration (if available)
   * pipeline editing and relaunching
   * automatic video texture embedding
   * properties control using gtk widgets for all (common) data types
   * pipeline graph (.dot format) displaying

## Usage

Will launch the gst-launch-compliant pipeline description:

```bash
gst-gengui videotestsrc ! xvimagesink sync=false
```

If no argument is given, it will launch the pipeline description found in the gstgengui/config.py file

## Installation

Install this package as a python egg: 

```bash
./setup.py install
```


## Options

Check the gstgengui/config.py file for options and examples.

The config file contains static declarations for:
* ignore-list: properties having one of these names will not be "introspected"
* pipeline_desc: gstreamer pipeline description, in gst-launch-like syntax. caps need to be set the following way (without the quotes):

```python
pipeline_desc = "videotestsrc ! video/x-raw, format=(string)YUY2, width=(int)320, height=(int)240, framerate=(fraction)15/1 ! videoconvert !  videobalance ! queue ! xvimagesink"
```

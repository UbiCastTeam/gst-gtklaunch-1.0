# gst-gtklaunch-1.0

gst-gtklaunch-1.0 is an utility for testing and controlling live GStreamer 1.0 pipelines and elements. It will inspect the specified pipeline to create the GTK GUI automagically using introspection.

![screenshot](https://raw.githubusercontent.com/UbiCastTeam/gst-gtklaunch/master/screenshot.png)

## Features

   * gst-launch-type syntax
   * pipeline controls: play, pause, stop, send_eos
   * pipeline states display: current state, current position, duration (if available)
   * pipeline editing and relaunching
   * automatic video sink embedding
   * foldable sidebar containing properties control widgets for most property types
   * pipeline graph (.dot format) displaying
   * if you add something like "tee. ! queue ! jpegenc ! fakesink name=dumpsink", you will be able to save jpeg thumbnails to disk

## Usage

Will launch the gst-launch-compliant pipeline description:

```bash
gst-gtklaunch-1.0 videotestsrc ! xvimagesink
```

If no argument is given, it will launch the pipeline description found in the gst-gtklaunch-1.0/config.py file

Adding "jpegenc ! fakesink name=dumpsink" will show a "take picture" button

```
gst-gtklaunch-1.0 videotestsrc ! tee name=tee ! queue ! xvimagesink tee. ! queue ! jpegenc ! fakesink name=dumpsink
```

## Installation

Install this package as a python egg: 

```bash
./setup.py install
```

gst-gtklaunch-1.0 currently requires (Ubuntu package names):
   * python3-gi
   * gir1.2-gtk-3.0
   * gir1.2-gstreamer-1.0
   * graphviz and xdot

An [Arch User Repository package](https://aur.archlinux.org/packages/gst-gtklaunch-1.0/) is also available.

## Options

Check the gst-gtklaunch-1.0/config.py file for options and examples.

The config file contains static declarations for:
* ignore-list: properties having one of these names will not be introspected
* pipeline_desc: gstreamer pipeline description, in gst-launch-like syntax. caps need to be set the following way (without the quotes):

```python
pipeline_desc = "videotestsrc ! video/x-raw, format=(string)YUY2, width=(int)320, height=(int)240, framerate=(fraction)15/1 ! videoconvert !  videobalance ! queue ! xvimagesink"
```

#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='gstgengui',
    version='0.1',
    author='Florent Thiery <fthiery@gmail.com>", "Dirk Van Haerenborgh <vhdirk@gmail.com>',
    url='https//github.ugent.be/gstreamer/gst-gengui',
    description="Utility for testing and controlling live GStreamer pipelines and elements",
    long_description=read('README.md'),
    license="LGPL",
    packages = find_packages(),
    
    entry_points=dict(gui_scripts=['gstgengui=gstgengui.gstgengui:main']),
    
    dependency_links = [
        "http://github.com/vhdirk/xdot.py/tarball/master"
    ],

    # This is true, but pointless, because easy_install PyGTK chokes and dies
    #install_requires=['', 'pycairo'],
)

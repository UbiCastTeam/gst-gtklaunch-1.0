#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='gst-gtklaunch-1.0',
    version='0.2',
    author='Florent Thiery <fthiery@gmail.com>", "Dirk Van Haerenborgh <vhdirk@gmail.com>',
    url='https://github.com/UbiCastTeam/gst_gtklaunch',
    description="Utility for testing and controlling live GStreamer pipelines and elements",
    long_description=read('README.md'),
    license="LGPL",
    packages = find_packages(),
    entry_points=dict(gui_scripts=['gst-gtklaunch-1.0=gst_gtklaunch.gst_gtklaunch:main']),
    dependency_links = [
        "http://github.com/vhdirk/xdot.py/tarball/master"
    ],          
    # This is true, but pointless, because easy_install PyGTK chokes and dies
    #install_requires=['', 'pycairo'],
)

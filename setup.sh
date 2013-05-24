#!/bin/sh
PYTHON_VER=`python -V 2>&1 | sed "s/Python \([0-9][0-9]*\)\.\([0-9][0-9]*\)\.[0-9][0-9]*/\1.\2/"`
PYTHON_DIR="python$PYTHON_VER/site-packages"

PREFIX=/usr/local
TARGET=$PREFIX/lib/$PYTHON_DIR/gstgengui
echo Detected python$PYTHON_VER, installing to $TARGET
sudo mkdir -p $PREFIX/lib/$PYTHON_DIR
sudo ln -sf `pwd`/gstgengui $TARGET 
sudo ln -sf `pwd`/gstgengui/gst-gengui.py $PREFIX/bin/gst-gengui
sudo chmod +x $PREFIX/bin/gst-gengui

#!/bin/sh
PYTHON_VER=`python -V 2>&1 | sed "s/Python \([0-9][0-9]*\)\.\([0-9][0-9]*\)\.[0-9][0-9]*/\1.\2/"`
PYTHON_24_DIR='python2.4/site-packages'
PYTHON_25_DIR='python2.5/site-packages'
PYTHON_26_DIR='python2.6/dist-packages'

if [ "$PYTHON_VER"  = "2.4" ]
then
    PYTHON_DIR=$PYTHON_24_DIR
elif [ "$PYTHON_VER"  = "2.5" ]
then
    PYTHON_DIR=$PYTHON_25_DIR
elif [ "$PYTHON_VER"  = "2.6" ]
then
    PYTHON_DIR=$PYTHON_26_DIR
fi

TARGET=/usr/local/lib/$PYTHON_DIR/gstgengui
echo Detected python$PYTHON_VER, installing to $TARGET
sudo ln -sf `pwd`/gstgengui $TARGET 
sudo ln -sf `pwd`/gstgengui/gst-gengui.py /usr/local/bin/gst-gengui
sudo chmod +x /usr/local/bin/gst-gengui

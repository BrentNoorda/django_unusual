#!/bin/bash
#
# set up environment for running django_unusual
# changes variables, to keep on exit run with a . , for example
#    # . ./setenv.sh

source venv/bin/activate

DYLD_LIBRARY_PATH=/Library/PostgreSQL/9.1/lib:$DYLD_LIBRARY_PATH
export DYLD_LIBRARY_PATH

PATH=/Library/PostgreSQL/9.1/bin:$PATH
export PATH

EVENT_NOKQUEUE=1
export EVENT_NOKQUEUE

LOCAL_DEV=True
export LOCAL_DEV

launchctl limit maxfiles 10000 20000

# wrap escapes in \[ and \] based on what I learned at http://hintsforums.macworld.com/showthread.php?t=17068
export PS1="\[\e[0;33m\]django_unsual \[\e[0;36m\][\w]#\[\e[0;33m\] "

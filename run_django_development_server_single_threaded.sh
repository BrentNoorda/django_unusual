#!/bin/bash
# RUN DJANGO DEVELOPMENT SERVER FORCING A SINGLE THREAD

# check that the environment looks correct and the directory is correct
DIR=$(cd $(dirname "$0"); pwd)
VENVDIR=$DIR/venv
if [ "$VENVDIR" != "$VIRTUAL_ENV" ]; then
   echo 'The environment seems wrong. Run ". ./setenv.sh" first'
   exit 1
fi

echo
python -c "import socket; print 'browse to 127.0.0.1:8000 or',socket.gethostbyname(socket.gethostname())+':8000';"
echo

#open http://localhost:8000/
python manage.py runserver 0.0.0.0:8000 --nothreading

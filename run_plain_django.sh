#!/bin/bash
#
# run a0pilot locally

# check that the environment looks correct and the directory is correct
DIR=$(cd $(dirname "$0"); pwd)
VENVDIR=$DIR/venv
if [ "$VENVDIR" != "$VIRTUAL_ENV" ]; then
   echo 'The environment seems wrong. Run ". ./setenv.sh" first'
   exit 1
fi

python manage.py runserver

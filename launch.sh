#!/bin/bash

function launch {
    export FLASKENV="development"
    python3 app.py
}



if [ "$1" ]; then
    case $1 in
        -l | --launch )             launch;;                               
    esac
    shift
else
	launch
fi

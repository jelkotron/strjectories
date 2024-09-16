#!/usr/bin/env bash

basedir=$(dirname $(realpath $0))
scriptdir=scripts
main=$basedir/$scriptdir/main.py
venv=$basedir/venv/bin/activate
geo=87x13+0+1025
title="STRWHAT"

# mate-terminal --geometry $geo --title $title -x sh -c ". $venv && python3 $basedir/$scriptdir/$main; bash"
x-terminal-emulator -title $title -geometry $geo -e 'sh -c ". '$venv' && python3 '$main'; bash";'   

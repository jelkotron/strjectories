#!/usr/bin/env bash

basedir=$(dirname $(realpath $0))
scriptdir=scripts
main=$basedir/$scriptdir/main.py
venv=$basedir/venv/bin/activate
geo=87x13+0+1025
title="STRWHAT"
desktop=$DESKTOP_SESSION
if [[ $DESKTOP_SESSION == *"mate"* ]]; then
    mate-terminal --geometry $geo --title $title -x sh -c ". $venv && python3 $main; bash"
    # x-terminal-emulator -T $title -geometry $geo -e 'sh -c "echo '$t' && . '$venv' && python3 '$main'; bash";'   
else
    if [[$DESKTOP_SESSION == *"LXDE"*]]; then
        lxterminal --geometry=$geo --title=$title -e 'sh -c "echo '$t' && . '$venv' && python3 '$main'; bash";'
    fi
fi

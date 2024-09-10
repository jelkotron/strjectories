#!/usr/bin/env bash

basedir=$(dirname $(realpath $0))
scriptdir=scripts
main=main.py
venv=$basedir/venv/bin/activate
geo=87x13+0+1025
title="STRWHAT"

mate-terminal --geometry $geo --title $title -x sh -c ". $venv && python3 $basedir/$scriptdir/$main; bash"

#!/usr/bin/env bash

basedir=$(dirname $(realpath $0))
scriptdir=scripts
main=main.py

geo=87x8+0+1025
title="STRWHAT"

mate-terminal --geometry $geo --title $title -x sh -c ". $basedir && python3 $basedir/$scriptdir/$main; bash"

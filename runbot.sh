#!/bin/sh

if [ "$#" -ne 1 ] || ! [ -d "$1" ]; then
    echo "Usage: $0 BOT" >&2
    exit 1
else
    irc3 $1/config.ini
fi

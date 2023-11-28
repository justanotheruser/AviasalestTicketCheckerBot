#!/bin/bash
if [ "$2" == "-s" ]; then
    if [ -z "$STY" ]; then
        exec screen -dmS air_bot /bin/bash "$0" "$1";
    fi
fi
cd "$1" || exit
source ~/.profile
poetry run python air_bot/main.py

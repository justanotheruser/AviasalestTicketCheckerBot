#!/bin/bash
if [ "$1" == "-s" ]; then
    if [ -z "$STY" ]; then
        exec screen -dm -S screenName /bin/bash "$0";
    fi
fi
poetry run python air_bot/main.py

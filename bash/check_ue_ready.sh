#!/bin/bash

# first check if softmodem is running
if ps x | grep ran.py > /dev/null; then
        echo "Softmodem running..."
else
        echo "Softmodem not running, exiting..."; exit 1
fi

stop_loop=false
ln_check="============================================"
max_trials=30
trials=0
while [ "$stop_loop" = false ]
do
##      echo "trial $trials"
        let "trials++"
        if [ $max_trials -eq $trials ]; then
                echo "Max trial reached, exiting..."
                exit 1
        fi
        ln=$(tail -2 last_log | head -1 | rev | cut -d ' ' -f1)
        if [ "$ln" = "$ln_check" ]; then
                echo "Softmodem ready"
                stop_loop=true # for future flexibility
                exit 0
        else
                echo "Softmodem not ready, waiting 1 second...";
                sleep 1
        fi
done

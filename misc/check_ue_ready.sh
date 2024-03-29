#!/bin/bash

# first check if softmodem is running
nproc=`ps x | grep ran.py | wc -l`
if  [ "$nproc" -gt 1 ]> /dev/null; then
        echo "Softmodem running..."
else
        echo "Softmodem not running, exiting..."; exit 1
fi

stop_loop=false
ln_check="============================================"
max_trials=60
trials=0
while [ "$stop_loop" = false ]
do
##      echo "trial $trials"
        let "trials++"
        nproc=`ps x | grep ran.py | wc -l`
        if  [ "$nproc" -lt 2 ]> /dev/null; then
                echo "Ran.py died, exiting..."
                exit 1
        fi
        if [ $max_trials -eq $trials ]; then
                echo "Max trial reached, exiting..."
                exit 1
        fi
        ln=$(tail -2 last_log 2> /dev/null | head -1 | rev | cut -d ' ' -f1)
        if [ $trials -eq 1 ]; then
                echo -n "Softmodem not ready";
        fi
        if [ "$ln" = "$ln_check" ]; then
                echo "" #new line after echo -n
                echo "Softmodem ready"
                stop_loop=true # for future flexibility
                exit 0
        else
                echo -n ".";
                sleep 1
        fi
done

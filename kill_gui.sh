#!/bin/bash

# Trova i processi che utilizzano la porta 8000
PROCESSES=$(lsof -i :8000 | awk 'NR!=1 {print $2}')

# Termina i processi trovati
if [ -n "$PROCESSES" ]; then
    echo "Terminating processes using port 8000:"
    for PID in $PROCESSES; do
        echo "Killing process with PID: $PID"
        kill -9 $PID
    done
else
    echo "No processes found using port 8000"
fi

# Trova i processi che utilizzano la porta 5173
PROCESSES=$(lsof -i :5173 | awk 'NR!=1 {print $2}')

# Termina i processi trovati
if [ -n "$PROCESSES" ]; then
    echo "Terminating processes using port 8000:"
    for PID in $PROCESSES; do
        echo "Killing process with PID: $PID"
        kill -9 $PID
    done
else
    echo "No processes found using port 8000"
fi
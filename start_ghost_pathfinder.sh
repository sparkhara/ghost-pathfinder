#!/bin/sh

set -ex

if [ -z $GHOST_PATHFINDER_LOGFILE ]; then
    echo "GHOST_PATHFINDER_LOGFILE not provided"
    exit 1
fi

if [ -z $GHOST_PATHFINDER_TIMESCALAR ]; then
    echo "GHOST_PATHFINDER_TIMESCALAR not provided"
    exit 1
fi

python /opt/ghost/ghost_pathfinder.py --file $GHOST_PATHFINDER_LOGFILE --time $GHOST_PATHFINDER_TIMESSCALAR

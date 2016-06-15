# ghost pathfinder

This application is a helper to playback a log file in realtime sending the
output to a local socket that is accepts on. The goal is to reduce the need
for a message queue when using the sparkhara applications. The
ghost-pathfinder then becomes a testing tool to that effort.

## usage

Simply running the `ghost_pathfinder.py` file will display its help. A
Dockerfile is provided to make building this as a container easier, it should
be noted that if the default log file option is being used then you must copy
your file must be copied to the root of this repository and be named
`logdata`.

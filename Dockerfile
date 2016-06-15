FROM python:2.7.11

ADD . /opt/ghost

CMD python /opt/ghost/ghost_pathfinder.py --file /opt/ghost/logdata

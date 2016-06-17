FROM openshift/python-27-centos7

ADD . /opt/ghost

CMD python /opt/ghost/ghost_pathfinder.py --file /opt/ghost/logdata

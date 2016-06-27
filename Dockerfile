FROM centos/python-27-centos7

ADD . /opt/ghost

CMD /opt/ghost/start_ghost_pathfinder.sh

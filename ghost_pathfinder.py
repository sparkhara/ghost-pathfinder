#!/bin/env python
'''
ghost whirlwind

this application will attempt to parse a log file and play back the log
messages as they occurred. meaning that it will read the date stamp from each
log line and attempt to calculcate the time difference and sleep between
sends. it will send the lines to a port specified on the command line.

this is intended to help feed the caravan master in cases where no zaqar
queue is present, or no services are available to provide live logs.

'''
import argparse
import collections
import datetime
import json
import os
import re
import socket
import time


LogEntry = collections.namedtuple('LogEntry', ['datestamp', 'body'])


def accept(port):
    print('awaiting connection')
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    send, send_addr = sock.accept()
    print('connection from: {}'.format(send_addr))
    return send, send_addr


def process_log_entry(logfile, filesize):
    '''
    attempt to read log lines and group them

    this will read the next line in the log file, if it does not begin
    with a recognized date stamp (YYYY-MM-DD HH:MM:SS.mmm) it will
    return None. if the line does begin with a recognized date stamp,
    the line will be added to the current log entry and the next line
    will be inspected for a date stamp. if the next line does not
    contain a date stamp, it will appended to the current entry. if the
    next line does contain a date stamp, the file position will be set
    to the start of that line and the function will return the current
    entry.

    '''
    def datestamp_match(line):
        DATESTAMP_RE = '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}'
        datestamp = line[:23]
        return re.match(DATESTAMP_RE, datestamp)

    nextline = logfile.readline()

    try:
        log_line = json.loads(nextline)
        datestamp = datetime.datetime.strptime(log_line.get('ts', ''),
                                               '%Y-%m-%d %H:%M:%S.%f')
    except:
        return None

    return LogEntry(datestamp, nextline)


def replace_newlines(logentries, separator='::newline::'):
    '''
    replace the newlines with a separator

    to reduce the possibility of logs getting split when sending over a
    socket, the newlines are replaced with a separator.

    '''
    for i, entry in enumerate(logentries):
        logentries[i] = LogEntry(entry.datestamp,
                                 entry.body.replace('\n', separator))


def ship_it(logentries, send):
    '''
    ship the log entries somewhere

    '''
    print('shipping {} entries'.format(len(logentries)))
    for entry in logentries:
        name = json.loads(entry.body).get('hn', 'ghost-pathfinder').replace('.', '-')
        bodydata = json.dumps({name: entry.body}) + '\n'
        if send is None:
            print(bodydata)
        else:
            s = send.send(bodydata)
            print('sent {} bytes from {} entries'.format(s, len(logentries)))


def main(args):
    if args.debug:
        print('running in debug')

    logfile = open(args.file, 'r')
    logfile.seek(0, os.SEEK_END)
    lfsize = logfile.tell()
    logfile.seek(0)

    logentries = []
    badentries = 0
    shippedentries = 0

    if args.port:
        send, send_addr = accept(args.port)
    else:
        send = None

    while logfile.tell() != lfsize:
        logentry = process_log_entry(logfile, lfsize)
        if logentry is None:
            badentries += 1
            continue
        if args.debug:
            print('processed')
            print(logentry)
        previous_datestamp = (logentry.datestamp if len(logentries) == 0
                              else logentries[-1].datestamp)
        datestamp_delta = logentry.datestamp - previous_datestamp
        if datestamp_delta.total_seconds() > 0:
            try:
                ship_it(logentries, send)
                shippedentries += len(logentries)
            except socket.error:
                send, send_addr = accept(args.port)
            logentries = []
            sleep_time = float(
                         datestamp_delta.total_seconds() / float(args.time)
                         if args.time != 1
                         else datestamp_delta.total_seconds())
            if args.debug:
                print('sleeping for {} seconds'.format(sleep_time))
            time.sleep(sleep_time)
        logentries.append(logentry)

    print('shipped {} valid entries'.format(shippedentries))
    print('found {} bad entries'.format(badentries))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='read a log file and send its lines to a socket')
    parser.add_argument('--file', help='the file to read', required=True)
    parser.add_argument('--port', help='the port to send on (default: 1984)',
                        type=int, default=1984)
    parser.add_argument('--time', help='the time scaling factor (default: 1)',
                        type=int, default=1)
    parser.add_argument('--debug', help='turn off socket sending',
                        action='store_true')
    args = parser.parse_args()

    try:
        main(args)
    except socket.error:
        pass

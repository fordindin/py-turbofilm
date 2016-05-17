#!/usr/bin/env python

import os
import re
import sys
import tempfile
import subprocess
import json
from subprocess import Popen, STDOUT
import metaWrapper
import config
import pickle
from lastunseen import listunseen

#if __name__ == "__main__": from turbofilm import wrkdir

class NotReadyYet(Exception):
    pass

def mplay(argv, latest=None, queue=None, t_name=None, offline=None):
    if not latest:
        if not t_name:
            ctime = []
            def wfunction(*argv):
                for f in argv[2]:
                    if os.path.isdir(f): continue
                    if os.path.splitext(f)[1] != '.mp4': continue
                    fpath=os.path.join(argv[1],f)
                    ctime.append((fpath,os.stat(fpath).st_ctime))

            def sort_cmp(a,b):
                if a[1] > b[1]: return 1
                elif a[1] == b[1]: return 0
                else: return -1
            os.path.walk(config.wrkdir, wfunction, None)
            ctime.sort(cmp=sort_cmp)
            try:
                latest = ctime[-1][0]
            except IndexError:
                print "There is no fetched episodes"
                sys.exit(1)
        else:
            t_dir = os.path.join(config.wrkdir, t_name)
            series = filter(lambda a: re.match(".*\.mp4",a), os.listdir(t_dir))
            series.sort()
            latest = os.path.join(t_dir,series[0])


    srt = os.path.splitext(latest)[0]+'.srt'

    try:
        metadata = metaWrapper.load_saved_meta(os.path.splitext(latest)[0]+'.meta')
    except IOError:
        print "Seems fetcher is not ready yet"
        return None

    args = [
            "mpv",
            latest,
            "-sub-file",
            srt,
            '-term-status-msg',
            "POSITION: |${=time-pos}|"
            ]
    args.extend(argv[1:])
    if metadata.has_key("lastpos"):
        if metadata["lastpos"] < 0:
            metadata["lastpos"] = 0
        args.extend(["-start", str(metadata["lastpos"])])

    devnull=open(os.devnull, "w")
    tmp = tempfile.NamedTemporaryFile()
    if queue: queue.put_nowait({"tmpfile": tmp.name})
    """
    tee = subprocess.Popen(["tee", tmp.name], stdin=subprocess.PIPE,
            stdout=devnull
            )
"""
    #p = Popen(args, stderr=tmp, stdout=devnull, close_fds=True)
    p = Popen(args, stderr=tmp, stdout=devnull)
    if queue: queue.put_nowait({"pid": p.pid})
    pid, sts = os.waitpid(p.pid, 0)
    tmp.flush()
    tmp.seek(0)
    quit_position=[0]
    l = tmp.readlines()
    if len(l) > 0:
        l = l[-1].strip()
        match = re.match("POSITION: \|(.*)\|", l)
        if match:
            quit_position = match.groups()
        """
    for l in tmp.readlines():
        if len(l.split(u'\033[J\r')) > 1:
            match = re.match("POSITION:\s|(.*)|", l.split(u'\033[J\r')[-2])
    """
    tmp.close()

    fd = open(os.path.splitext(latest)[0]+'.meta', "w+")
    metadata["lastpos"]=float(quit_position[0]) - 5
    fd.write(json.dumps(metadata))
    fd.close()


    if float(quit_position[0])/float(metadata["duration"]) > 0.98:
        response = metaWrapper.watchEpisode(metadata["eid"], offline=offline)
        if response == {'page': ''}:
            print '\n\nEpisode has been watched'
            print 'Cleanup...'
            for e in ('.meta','.mp4', '.srt', '.log'):
                try:
                    os.remove(os.path.splitext(latest)[0]+e)
                except OSError: pass
            if queue: queue.put({"cleaned_up":True})
            if not offline:
                print listunseen()
    if queue: queue.put({"pos":float(quit_position[0])})
    #tee.stdin.close()
    return float(quit_position[0])

if __name__ == '__main__':
    mplay(sys.argv)

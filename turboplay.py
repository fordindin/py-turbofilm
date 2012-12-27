#!/usr/bin/env python

import os
import re
import sys
import tempfile
import subprocess
import json
from subprocess import Popen

#selfpath = os.path.realpath(sys.argv[0])
#selfdir = os.path.dirname(selfpath)
#if not selfdir in sys.path: sys.path.append(selfdir)
import remoteMeta
if __name__ == "__main__": from turbofilm import wrkdir

def mplay(argv, queue=None):
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
		os.path.walk(wrkdir, wfunction, None)
		ctime.sort(cmp=sort_cmp)
		latest = ctime[-1][0]
		srt = os.path.splitext(latest)[0]+'.srt'

		fd = open(os.path.splitext(latest)[0]+'.meta')
		metadata = json.load(fd)
		fd.close()
		# neat trick to duplicate stdout content to tempfile
		#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
		#os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
		#os.dup2(tee.stdin.fileno(), sys.stderr.fileno())

		args = [
				"mplayer",
				latest,
				"-sub",
				srt
				]
		args.extend(argv[1:])
		if metadata.has_key("lastpos"):
				args.extend(["-ss", str(metadata["lastpos"])])

		tmp = tempfile.NamedTemporaryFile()
		tee = subprocess.Popen(["tee", tmp.name], stdin=subprocess.PIPE)
		p = Popen(args, stdout=tee.stdin)
		pid, sts = os.waitpid(p.pid, 0)
		tmp.flush()
		tee.stdin.flush()
		tmp.seek(0)
		quit_position=0
		for l in tmp.readlines():
				if len(l.split(u'\033[J\r')) > 1:
						match = re.match("A:\s*[0-9.]*\s*V:\s*([0-9.]*)\s*A-V:", l.split(u'\033[J\r')[-2])
						if match:
								quit_position = match.groups()

		tmp.close()
		fd = open(os.path.splitext(latest)[0]+'.meta', "w+")
		if float(quit_position[0])/float(metadata["duration"]) < 0.98:
						metadata["lastpos"]=float(quit_position[0]) - 5
						fd.write(json.dumps(metadata))
		else:
				if metadata.has_key("lastpos"):
						del(metadata["lastpos"])
				fd.write(json.dumps(metadata))
				print remoteMeta.watchEpisode(metadata["eid"])
		#fd.truncate()
		fd.close()
		if queue: queue.put(float(quit_position[0]))
		else: return float(quit_position[0])

if __name__ == '__main__':
		mplay(sys.argv)

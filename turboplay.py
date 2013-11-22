#!/usr/bin/env python

import os
import re
import sys
import tempfile
import subprocess
import json
from subprocess import Popen
import metaWrapper
import config

#if __name__ == "__main__": from turbofilm import wrkdir

def mplay(argv, latest=None, queue=None):
		if not latest:
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
		srt = os.path.splitext(latest)[0]+'.srt'

		metadata = metaWrapper.load_saved_meta(os.path.splitext(latest)[0]+'.meta')

		args = [
				"mplayer",
				latest,
				"-sub",
				srt
				]
		args.extend(argv[1:])
		if metadata.has_key("lastpos"):
				args.extend(["-ss", str(metadata["lastpos"])])

		devnull=open(os.devnull, "w")
		tmp = tempfile.NamedTemporaryFile()
		if queue: queue.put_nowait({"tmpfile": tmp.name})
		tee = subprocess.Popen(["tee", tmp.name], stdin=subprocess.PIPE,
						stdout=devnull,
						)
		p = Popen(args, stdout=tee.stdin, stderr=devnull)
		if queue: queue.put_nowait({"pid": p.pid})
		pid, sts = os.waitpid(p.pid, 0)
		tmp.flush()
		tee.stdin.flush()
		tmp.seek(0)
		quit_position=[0]
		for l in tmp.readlines():
				if len(l.split(u'\033[J\r')) > 1:
						match = re.match("A:\s*[0-9.]*\s*V:\s*([0-9.]*)\s*A-V:", l.split(u'\033[J\r')[-2])
						if match:
								quit_position = match.groups()

		tmp.close()

		fd = open(os.path.splitext(latest)[0]+'.meta', "w+")
		metadata["lastpos"]=float(quit_position[0]) - 5
		fd.write(json.dumps(metadata))
		fd.close()


		if float(quit_position[0])/float(metadata["duration"]) > 0.98:
				response = metaWrapper.watchEpisode(metadata["eid"])
				if response == {'page': ''}:
						print '\n\nEpisode has been watched'
						print 'Cleanup...'
						for e in ('.meta','.mp4', '.srt', '.log'):
								try:
										os.remove(os.path.splitext(latest)[0]+e)
								except OSError: pass
		if queue: queue.put({"pos":float(quit_position[0])})
		if queue: queue.put({"cleaned_up":True})
		tee.stdin.close()
		return float(quit_position[0])

if __name__ == '__main__':
		mplay(sys.argv)

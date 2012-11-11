#!/usr/bin/env python

import os
import sys
from subprocess import Popen

ctime = []
def wfunction(*argv):
		for f in argv[2]:
				if os.path.isdir(f): continue
				fpath=os.path.join(argv[1],f)
				ctime.append((fpath,os.stat(fpath).st_ctime))
os.path.walk("/Users/dindin/tmp/turbofilm", wfunction, None)

def sort_cmp(a,b):
		if a[1] > b[1]: return 1
		elif a[1] == b[1]: return 0
		else: return -1

ctime.sort(cmp=sort_cmp)
latest = ctime[-1][0]

args = [
		"mplayer",
		latest]
args.extend(sys.argv[1:])

Popen(args)

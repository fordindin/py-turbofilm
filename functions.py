#!/usr/bin/env python

import os
import re

def hangmon(tmpfilename, mplayer_pid):
		if tmpfilename and os.path.exists(tmpfilename):
				offset = os.stat(tmpfilename).st_size - 150
				tmpfile = open(tmpfilename, "r")
				tmpfile.seek(offset)
				d = tmpfile.read()
				tmatch = re.match(".*A-V:\s*([0-9\-\.]+).*", d)
				#if tmatch: print float(tmatch.groups()[0])
				if tmatch and float(tmatch.groups()[0]) > 0.5 and mplayer_pid:
						print "Killing mplayer"
						#print "diff: %s" % tmatch.groups()[0]
						os.kill(mplayer_pid, 15)

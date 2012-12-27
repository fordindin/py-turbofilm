#!/usr/bin/env python

from subprocess import Popen, PIPE
import sys
import os
from cdn_url import cdn_url

maxretry = 5

def fetcher(metadata, iasid, dir_name, quality,  silent=False):
		sts = 1
		trycount = 0
		while sts != 0:
				if silent:
						stdout=PIPE
						stdin=None
						stderr=PIPE
						close_fds=True
				else:
						stdout=sys.stdout
						stdin=sys.stdin
						stderr=sys.stderr
						close_fds=False
						print "Try number %d" % trycount

				#retcode = os.execv(
				#		)["subtitles"]["sources"]["en"
				if silent:
						p = Popen(
										["wget",
								"-c", "-O", dir_name+".mp4",
								cdn_url(iasid,
										metadata["eid"],
										metadata["sources2"][quality],
										0,
										"en")
								],
								stdout=stdout,
								stdin=stdin,
								stderr=stderr,
								close_fds=close_fds,
						)
						#p.communicate()
						pid, sts = os.waitpid(p.pid, 0)
						#p.wait()
				else:
						p = Popen(
										["wget",
								"-c", "-O", dir_name+".mp4",
								cdn_url(iasid,
										metadata["eid"],
										metadata["sources2"][quality],
										0,
										"en")
								],
						)
						pid, sts = os.waitpid(p.pid, 0)
				trycount += 1
				if trycount > maxretry: break

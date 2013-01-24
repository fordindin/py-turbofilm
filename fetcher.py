#!/usr/bin/env python

from subprocess import Popen, PIPE
import sys
import os
from cdn_url import cdn_url
import config

def fetcher(metadata, iasid, dir_name, quality,  silent=False):
		sts = 1
		trycount = 0
		while sts != 0:
				print "Try number %d" % trycount

				wget_args = [
								"wget",
								"-c", "-O", dir_name+".mp4",
								"--no-check-certificate",
								cdn_url(iasid,
										metadata["eid"],
										metadata["sources2"][quality],
										0,
										"en")
								]

				kwargs = { }

				if silent:
						kwargs.update({
								"stdout" : PIPE,
								"stdin" : None,
								"stderr" : PIPE,
								"close_fds" : True,
								})

				print wget_args
				p = Popen( wget_args, **kwargs )
				pid, sts = os.waitpid(p.pid, 0)

				trycount += 1
				if trycount > config.max_fetch_retry: break
		os.utime(dir_name+".mp4", None)

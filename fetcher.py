#!/usr/bin/env python

from subprocess import Popen, PIPE
import sys
import os
from cdn_url import cdn_url
import config
import urllib2

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

				#print wget_args
				p = Popen( wget_args, **kwargs )
				pid, sts = os.waitpid(p.pid, 0)

				trycount += 1
				if trycount > config.max_fetch_retry: break
		os.utime(dir_name+".mp4", None)

def pfetcher(metadata, iasid, dir_name, quality,  silent=False, bufsize=524288,
				outdata=None):
		fpath = dir_name+".mp4"
		if os.path.isfile(fpath):
				size = os.stat(fpath).st_size
		else:
				size = 0
		f = open(fpath, "a")
		req = urllib2.Request(
								cdn_url(iasid,
										metadata["eid"],
										metadata["sources2"][quality],
										0,
										"en")
								)
		req.headers['Range'] = 'bytes=%s-%s' % (size, metadata["sizes"][quality])
		r = urllib2.urlopen(req)

		buf = r.read(bufsize)
		sec = float(size)/metadata["bitrate"]
		if outdata:
				outdata.updata({"size":size, "sec":sec})
		if not silent:
				sys.stdout.write("% 6d seconds fetched % 6d seconds total (% 3d%%)" % (
						int(sec),
						int(metadata["duration"]),
						int(float(sec)/float(metadata["duration"])*100))
						)
				sys.stdout.flush()
		while buf:
				size+=bufsize
				f.write(buf)
				f.flush()
				if not silent:
						sys.stdout.write("\b"*50)
						sys.stdout.flush()
						sec = float(size)/metadata["bitrate"]
						sys.stdout.write("% 6d seconds fetched % 6d seconds total (% 3d%%)" % (
								int(sec),
								int(metadata["duration"]),
								int(float(sec)/float(metadata["duration"])*100))
								)
						sys.stdout.flush()
				buf  = r.read(bufsize)

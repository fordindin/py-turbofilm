#!/usr/bin/env python

from subprocess import Popen, PIPE
import sys
import os
from cdn_url import cdn_url
import config
import urllib2
import time


def fetcher(metadata, iasid, file_base, quality,  silent=False):
		sts = 1
		trycount = 0
		while sts != 0:
				print "Try number %d" % trycount

				wget_args = [
								"wget",
								"-c", "-O", file_base+".mp4",
								"--no-check-certificate",
								cdn_url(metadata["iasid"],
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
		os.utime(file_base+".mp4", None)

def pfetcher(metadata, file_base, quality, silent=False, bufsize=524288,
				outdata=None, queue=None):
		#print ""
		global gdict
		gdict={}
		gdict['relative_speed'] = 0
		gdict['start_time'] = time.time()
		gdict['current_time'] = time.time()
		gdict['previous_time'] = time.time()
		gdict['previous_sec'] = 0

		def pprint(metadata):
				w_template="% 6d seconds fetched % 6d seconds total (% 3d%%) % 4d spent % 5d sec % 7s"
				if not silent:
						global gdict
						gdict['previous_time'] = gdict['current_time']
						gdict['current_time'] = time.time()
						t_time = gdict['current_time'] - gdict['start_time']
						this_session_fetched_sec = float(size - initial_size)/metadata["bitrate"]
						gdict['prevous_sec'] = this_session_fetched_sec
						total_sec = float(size)/metadata["bitrate"]
						delta_time = gdict['current_time'] - gdict['start_time']

						sys.stdout.write("\b"*len(w_template % (0,0,0,0,0," "*7)))

						gdict['relative_speed'] = this_session_fetched_sec - delta_time

						if gdict['relative_speed'] > 0:
								smod = "ahead"
								out = gdict['relative_speed']
						elif gdict['relative_speed'] < 0:
								smod = "behind"
								out = -gdict['relative_speed']
						elif gdict['relative_speed'] == 0:
								smod = " "
								out = gdict['relative_speed']

						sys.stdout.write(w_template % (
								int(total_sec),
								int(metadata["duration"]),
								int(float(total_sec)/float(metadata["duration"])*100),
								int(t_time),
								int(out),
								smod,
								))
						sys.stdout.flush()
						if os.getenv("TMUX"):
								w_template="\033k%s\033\\" % w_template
								sys.stdout.write(w_template % (
										int(total_sec),
										int(metadata["duration"]),
										int(float(total_sec)/float(metadata["duration"])*100),
										int(t_time),
										int(out),
										smod,
										))

		fpath = file_base+".mp4"
		initial_size = None
		if os.path.isfile(fpath):
				size = os.stat(fpath).st_size
		else:
				size = 0
		if not initial_size:
				initial_size = size
		if size >= int(metadata["sizes"][quality])-1024:
				print "Already fetched"
				if queue: queue.put(True)
				return True
		f = open(fpath, "a")
		u = cdn_url(metadata["iasid"],
										metadata["eid"],
										metadata["sources2"][quality],
										0,
										"en")
		req = urllib2.Request(u)
		req.headers['Range'] = 'bytes=%s-%s' % (size, metadata["sizes"][quality])
		trycount = 0
		
		while trycount <= config.max_fetch_retry:
				try:
						trycount += 1
						r = urllib2.urlopen(req)
						break
				except (urllib2.HTTPError,urllib2.URLError) as ue:
						if ue.__class__.__name__ == 'URLError':
								print "URL error on URL: "+u
								print ue.args
						if ue.__class__.__name__ == 'HTTPError':
								print "HTTP error on URL: "+u
								print ue.args
						#if ue.code == 404:
						continue

		if trycount >= config.max_fetch_retry:
				print "Reached: config.max_fetch_retry=%s" % config.max_fetch_retry
				sys.exit(1)
		buf = r.read(bufsize)
		sec = float(size)/metadata["bitrate"]
		#if outdata:
		#		outdata.updata({"size":size, "sec":sec})
		pprint(metadata)
		while buf:
				size+=bufsize
				f.write(buf)
				f.flush()
				pprint(metadata)
				buf  = r.read(bufsize)
		print "Fetch done"
		sec = 0
		if queue: queue.put(True)
		return True

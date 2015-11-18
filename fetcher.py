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
		gdict['r_speed'] = 0
		gdict['start_time'] = time.time()
		gdict['current_time'] = time.time()
		gdict['previous_time'] = time.time()
		gdict['previous_sec'] = 0
		w_template="% 6d seconds fetched % 6d seconds total (% 3d%%) % 4d spent % 5d sec % 7s"
		def pprint(metadata):
				if not silent:
						global gdict
						gdict['previous_time'] = gdict['current_time']
						gdict['current_time'] = time.time()
						t_time = gdict['current_time'] - gdict['start_time']
						sys.stdout.write("\b"*len(w_template % (0,0,0,0,0," "*7)))
						this_session_sec = float(size - initial_size)/metadata["bitrate"]
						this_probe_sec = this_session_sec - gdict['previous_sec']
						gdict['prevous_sec'] = this_session_sec
						sec = float(size)/metadata["bitrate"]
						delta = gdict['current_time'] - gdict['previous_time']
						if int(round(delta)) != 0:
								gdict['r_speed']= gdict['prevous_sec']/delta
						if gdict['r_speed'] > 0:
								smod = "ahead"
								out = gdict['r_speed']
						elif gdict['r_speed'] < 0:
								smod = "behind"
								out = -gdict['r_speed']
						elif gdict['r_speed'] == 0:
								smod = " "
								out = gdict['r_speed']
						sys.stdout.write(w_template % (
								int(sec),
								int(metadata["duration"]),
								int(float(sec)/float(metadata["duration"])*100),
								int(t_time),
								int(out),
								smod,
								))
						sys.stdout.flush()

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
				except (urllib2.HTTPError,urllib2.URLError) as ue:
						if ue.__class__.__name__ == 'URLError':
								print "URL error on URL: "+u
						if ue.__class__.__name__ == 'HTTPError':
								print "HTTP error on URL: "+u
								print u
						#if ue.code == 404:
						continue

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

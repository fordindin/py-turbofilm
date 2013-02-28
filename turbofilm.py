#!/usr/bin/env python

import GetPage
from HTMLParser import HTMLParser
from urllib2 import unquote
from wierd_b64_decode import w_base64_decode as wb64
from cdn_url import cdn_url
import xml2obj
from xml2srt import fetch_sub
import os
import re
import sys
import json
from subprocess import Popen, PIPE
from lastunseen import lastunseen, listunseen
from random import Random
import threading
import time
import Queue
import turboplay
import time
from fetcher import fetcher, pfetcher
import config

#selfpath = os.path.realpath(sys.argv[0])
#selfdir = os.path.dirname(selfpath)
#sys.path.append(selfdir)

wrkdir = config.wrkdir
turboplay.wrkdir = wrkdir
sdata_RE = config.sdata_RE

def usage(selfname):
		print """Usage:
\t%s unseen
\t\tor
\t%s [-lq] SeriesName
\t\tor
\t%s [-lq] SeriesName SeasonNumber EpisodeNumber\n""" % tuple([os.path.basename(selfname)]*4)
		sys.exit(1)

class MyHTMLParser(HTMLParser):
		metadata = None
		def handle_starttag(self, tag, attrs):
				if ("id", "metadata") in attrs:
						for a in attrs:
								if a[0] == 'value':
										self.metadata=a[1]

def main(argv):
		if not os.path.isdir(wrkdir): os.mkdir(wrkdir)
		quality="hq"
		playargs=[]
		play=False
		if "-lq" in argv:
				quality = "default"
				argv.pop(argv.index("-lq"))
		if len(argv) > 1 and argv[1] == 'unseen':
				print listunseen()
				sys.exit(0)
		if "play" in argv:
				play=True
				playindex=argv.index("play")
				for i in range(playindex, len(argv)):
						playargs.append(argv.pop(playindex))
				playargs.pop(0)
		if len(argv) == 1:
				turboplay.mplay(playargs)
				sys.exit(0)

		get_lastunseen=False

		if argv[1] == 'runseen':
				tr = filter(lambda a: a[0]==3, listunseen(retlist=True))
				r = Random()
				get_lastunseen=True
				t_name = r.choice(tr)[1]

		if len(argv) == 2:
				series_data = sdata_RE.match(argv[1])
				if series_data:
						t_name, season, number = series_data.groups()
				else:
						get_lastunseen=True
						selfname, t_name = argv
		elif len(argv) == 4:
				selfname, t_name, season, number = argv
		else: usage(argv[0])

		if get_lastunseen:
				url = lastunseen(t_name)
				series_data = config.sdata_RE.match(url)
				t_name, season, number = series_data.groups()
		else:
				url =  sdata_TMPL % (config.proto, t_name, season,
						number)
				

		s_dir = os.path.join(wrkdir, t_name)
		fname_base = "S%02dE%02d" % (int(season), int(number))

		dir_name = os.path.join(s_dir, fname_base)
		parser = MyHTMLParser()
		page = GetPage.getpage(url)["page"]
		iasid = GetPage.p.check_ssid()
		parser.feed(page)
		xml_metadata = wb64(unquote(parser.metadata))
		print "Got XML" # xml_metadata

		os.chdir(wrkdir)
		if not os.path.exists(s_dir):
				os.mkdir(s_dir)

		metadata = xml2obj.xml2obj(xml_metadata)
		metadata["fetched_quality"] = quality
		if not os.path.isfile(dir_name+".meta") or os.stat(dir_name+".meta").st_size == 0:
				fd = open(dir_name+".meta", "w")
				fd.write(json.dumps(metadata))
				fd.close()
		metadata.update({'bitrate': float(metadata["sizes"][quality])/float(metadata['duration'])})
		print "bitrate: %s byte/sec" % metadata['bitrate']
		try:
				print "Got metadata" # metadata
				fetch_sub(metadata["subtitles"]["sources"]["en"], dir_name+".srt")
				print "Got subtitles"
		except KeyError:
				print "Subtitles not found"


		if play:
				pos = 0
				queue = Queue.Queue()
				outdata = {}
				fetch_th = threading.Thread(target=pfetcher, args=(metadata, iasid, dir_name,
						quality),
						kwargs={"silent":True, "outdata":outdata})
				fetch_th.start()
				wait_time = 1
				total_fetched_sec = 0
				nprobes = 0
				average = 0
				asize = 0
				logfd = open(dir_name+".log", "a+")
				saved_metadata = turboplay.load_saved_meta(dir_name+".meta")
				play_th = threading.Thread(target=lambda a: a)
				"""
				while float(pos)/float(metadata["duration"]) < 0.98 and (fetch_th.isAlive() or
								fetch_done):
						total = average*nprobes
						if not os.path.isfile(dir_name+".mp4"):
								bsize = 0
						else:
								bsize = os.stat(dir_name+".mp4").st_size
						if not fetch_done: time.sleep(wait_time)
						asize = os.stat(dir_name+".mp4").st_size
						if asize == bsize and fetch_th.isAlive(): continue
						if bsize >= float(metadata["sizes"][quality]):
								fetch_done = True
						else:
								fetch_done = False
						fetch_per_sec = float(asize-bsize)/float(metadata["bitrate"])/wait_time
						nprobes+=1
						if nprobes % 15 == 0:
								print >> logfd, "%s : total time fetched: %s" % (
										time.strftime("%H:%M %d-%m-%Y"), total)
								print >> logfd, "%s : average fetch speed (sps): %s" % (
										time.strftime("%H:%M %d-%m-%Y"), average)
								print >> logfd, "%s : last period fetch speed (sps): %s" % (
										time.strftime("%H:%M %d-%m-%Y"), fetch_per_sec)
								print >> logfd, "%s : last period fetch speed (kbps): %s" % (
										time.strftime("%H:%M %d-%m-%Y"), float(asize-bsize)/wait_time/1024)
								print >> logfd, "%s : total size (kbps): %s" % (
										time.strftime("%H:%M %d-%m-%Y"), asize/1024)
								if saved_metadata.has_key("lastpos"):
										print >> logfd, "%s : last position (kb): %s" % (
												time.strftime("%H:%M %d-%m-%Y"),
												saved_metadata["lastpos"]*metadata["bitrate"]/1024)
								logfd.flush()
						average = (total+fetch_per_sec)/nprobes
						if not total and not fetch_done:
								continue
						#print average
						if (average > 3 and nprobes > 1) and not play_th.isAlive() or fetch_done:
								play_th = threading.Thread(target=turboplay.mplay, args=(playargs,),
												kwargs={"latest": dir_name+".mp4", "queue":queue})
								play_th.start()
								#play_th.join()
								if not queue.empty():
										pos = queue.get()
										"""
		else:
				pfetcher(metadata, iasid, dir_name, quality)


if __name__ == "__main__":
		main(sys.argv)


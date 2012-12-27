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
from fetcher import fetcher

#selfpath = os.path.realpath(sys.argv[0])
#selfdir = os.path.dirname(selfpath)
#sys.path.append(selfdir)


wrkdir = "%s/turbofilm" % os.getenv("HOME")
turboplay.wrkdir = wrkdir

def usage(selfname):
		print """Usage:
\t%s unseen
\t%s [-lq]  http://turbofilm.tv/Path/To/Episode
\t\tor
\t%s [-lq] SeriesName
\t\tor
\t%s [-lq] SeriesName SeasonNumber EpisodeNumber\n""" % tuple([os.path.basename(selfname)]*4)
		sys.exit(1)

class MyHTMLParser(HTMLParser):
		metadata=None
		def handle_starttag(self, tag, attrs):
				if ("id", "metadata") in attrs:
						for a in attrs:
								if a[0] == 'value':
										self.metadata=a[1]

def main(argv):
		if not os.path.isdir(wrkdir): os.mkdir(wrkdir)
		quality="hq"
		play=False
		if "-lq" in argv:
				quality = "default"
				argv.pop(argv.index("-lq"))
		if argv[1] == 'unseen':
				print listunseen()
				sys.exit(0)
		if "play" in argv:
				play=True
				playindex=argv.index("play")
				playargs=[]
				for i in range(playindex, len(argv)):
						playargs.append(argv.pop(playindex))
				playargs.pop(0)

		get_lastunseen=False

		if argv[1] == 'runseen':
				tr = filter(lambda a: a[0]==3, listunseen(retlist=True))
				r = Random()
				get_lastunseen=True
				t_name = r.choice(tr)[1]

		if len(argv) == 2:
				series_data = re.match("http://turbofilm.tv/Watch/(.*)/Season(.*)/Episode(.*)",argv[1])
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
				series_data = re.match("http://turbofilm.tv/Watch/(.*)/Season(.*)/Episode(.*)",url)
				t_name, season, number = series_data.groups()
		else:
				url = "http://turbofilm.tv/Watch/%s/Season%s/Episode%s" % (t_name, season,
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
		fd = open(dir_name+".meta", "w")
		fd.write(json.dumps(metadata))
		fd.close()
		try:
				print "Got metadata" # metadata
				fetch_sub(metadata["subtitles"]["sources"]["en"], dir_name+".srt")
				print "Got subtitles"
		except KeyError:
				print "Subtitles not found"


		if play:
				pos = 0
				queue = Queue.Queue()
				fetch_th = threading.Thread(target=fetcher, args=(metadata, iasid, dir_name, quality),
						kwargs={"silent":True})
				fetch_th.start()
				time.sleep(5)
				while float(pos)/float(metadata["duration"]) < 0.98 and fetch_th.isAlive():
						play_th = threading.Thread(target=turboplay.mplay, args=(playargs,),
								kwargs={"queue":queue})
						play_th.start()
						play_th.join()
						if not queue.empty():
								pos = queue.get()
		else:
				fetcher(metadata, iasid, dir_name, quality)


if __name__ == "__main__":
		main(sys.argv)


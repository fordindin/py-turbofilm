#!/usr/bin/env python

from xml2srt import fetch_sub
from metaWrapper import get_metadata,watchEpisode
import os
import re
import sys
import json
from subprocess import Popen, PIPE
from lastunseen import listunseen, NoMoreSeries
from random import Random
import threading
import time
import Queue
import turboplay
import time
from fetcher import fetcher, pfetcher
import metaWrapper
import config
from functions import hangmon
import pickle

#selfpath = os.path.realpath(sys.argv[0])
#selfdir = os.path.dirname(selfpath)
#sys.path.append(selfdir)

#wrkdir = config.wrkdir
#turboplay.wrkdir = wrkdir
#sdata_RE = config.sdata_RE

def usage(selfname):
		print """Usage:"""
		sys.exit(1)

def main(argv):
		if not os.path.isdir(config.wrkdir): os.mkdir(config.wrkdir)
		os.chdir(config.wrkdir)
		quality=config.quality
		playargs=[]
		play=False
		offline=False
		offlineplay=False
		proxy=False
		if "-lq" in argv:
				quality = "default"
				argv.pop(argv.index("-lq"))
		if "-hq" in argv:
				quality = "hq"
				argv.pop(argv.index("-hq"))
		if "-proxy" in argv:
				proxy = True
				argv.pop(argv.index("-proxy"))
		if len(argv) > 1 and argv[1] == 'unseen':
				print listunseen()
				sys.exit(0)
		if "-sub_lang" in argv:
				ix = argv.index("-sub_lang")
				argv.pop(ix)
				config.sub_lang = argv.pop(ix)
		if "play" in argv:
				play=True
				playindex=argv.index("play")
				for i in range(playindex, len(argv)):
						playargs.append(argv.pop(playindex))
				playargs.pop(0)
		if "offline" in argv:
				offline=True
				offindex = argv.index("offline")
				offnum = 0
				if len(argv) > 3:
						offnum = argv[offindex+1]
						argv.pop(offindex)
				argv.pop(offindex)
		if "offlineplay" in argv:
				offlineplay=True
				playindex=argv.index("offlineplay")
				for i in range(playindex, len(argv)):
						playargs.append(argv.pop(playindex))
				playargs.pop(0)

		if "viewmap" in argv:
				from viewmap import viewmap
				viewmap()
				sys.exit(0)

		if "fullunseen" in argv:
				import viewmap
				viewmap.listunseen()
				sys.exit(0)

		if "compactunseen" in argv:
				for e in listunseen(retlist=True):
						print e[1]
				sys.exit(0)

		if len(argv) == 1:
				turboplay.mplay(playargs)
				sys.exit(0)

				tr = filter(lambda a: a[0]==3, listunseen(retlist=True))
				r = Random()
				t_name = r.choice(tr)[1]

		if len(argv) == 2:
				selfname, t_name = argv

		else: usage(argv[0])
		if not os.path.isdir(os.path.join(config.wrkdir,t_name)): os.mkdir(os.path.join(config.wrkdir,t_name))

		play_th = threading.Thread(target=lambda a: a)
		fetch_th = threading.Thread(target=lambda a: a)
		play_queue = Queue.Queue()
		fetch_queue = Queue.Queue()
		mplayer_pid = None

		logfd = sys.stdout

		if not offlineplay:
				try:
						f = open(config.offline_store)
						d = pickle.load(f)
						f.close()
				except IOError:
						d = []
				td = list(d)
				for e in td:
						r = watchEpisode(e["eid"])
						if r == {'page': ''}:
								d.pop(d.index(e))
				f = open(config.offline_store,"w+")
				pickle.dump(d,f)
				f.close()
		if play:
				fetch_done = False
				metadata_fetch_done = False
				sub_fetch_done = False
				pos = nprobes = average = asize = 0
				tmpfilename = None

				while True:
						"""
						if play_th.is_alive() and mplayer_pid and tmpfilename:
								hangmon(tmpfilename, mplayer_pid) """

						if not metadata_fetch_done:
								try:
										metadata, file_base = get_metadata(t_name, quality)
										quality = metadata["fetched_quality"]
										metadata_fetch_done = True
										print "Got metadata" # metadata
								except NoMoreSeries:
										print "No more series"
										sys.exit(0)

						if not sub_fetch_done:
								try:
										if metadata_fetch_done:
												fetch_sub(metadata["subtitles"]["sources"][config.sub_lang], file_base+".srt")
												print "Got subtitles"
								except KeyError:
										print "Subtitles not found"
								sub_fetch_done = True

						if not fetch_th.is_alive() and not fetch_done:
								if metadata_fetch_done:
										fetch_th = threading.Thread(target=pfetcher, args=(metadata, file_base,
												quality),
												kwargs={"silent":False, "queue" : fetch_queue})
										fetch_th.daemon = True
										fetch_th.start()
										#time.sleep(config.wait_time*10)

						if not fetch_queue.empty():
								fetch_done = fetch_queue.get()

						if not play_queue.empty():
								obj = play_queue.get()
								if obj.has_key("pos"): pos = obj["pos"]
								if obj.has_key("tmpfile"): tmpfilename = obj["tmpfile"]
								if obj.has_key("pid"): mplayer_pid = obj["pid"]
								if obj.has_key("cleaned_up"):
										fetch_done = False
										sub_fetch_done = False
										metadata_fetch_done = False
										continue

						if not play_th.is_alive() and os.path.exists(file_base+".mp4") and os.stat(file_base+".mp4").st_size > 0:
								play_th = threading.Thread(target=turboplay.mplay, args=(playargs,),
												kwargs={"latest": file_base+".mp4",
														"queue":play_queue})
								play_th.start()
								print "Playing: \n%s Season %s Episode %s" % (t_name,
										metadata["season"], metadata["number"])
						time.sleep(config.wait_time)

		elif offline:
				offset = 0
				while offnum > offset or offnum == 0:
						metadata, file_base = get_metadata(t_name, quality, offset=offset)
						print "Fetching for offline: \n%s Season %s Episode %s" % (t_name,
								metadata["season"], metadata["number"])
						try:
								fetch_sub(metadata["subtitles"]["sources"][config.sub_lang], file_base+".srt")
						except KeyError:
								print "Subtitles not found"
						pfetcher(metadata, file_base, quality)
						offset += 1
						#print t_name, metadata["season"], metadata["number"]
					
		elif offlineplay:
				while True:
						turboplay.mplay(playargs, t_name=t_name, offline=True)
		else:
				metadata, file_base = get_metadata(t_name, quality)
				print "Got metadata" # metadata

				try:
						fetch_sub(metadata["subtitles"]["sources"][config.sub_lang], file_base+".srt")
						print "Got subtitles"
				except KeyError:
						print "Subtitles not found"
				pfetcher(metadata, file_base, quality)


if __name__ == "__main__":
		main(sys.argv)


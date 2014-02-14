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
		print """Usage:
\t%s unseen
\t\tor
\t%s [-lq] SeriesName
\t\tor
\t%s [-lq] SeriesName SeasonNumber EpisodeNumber\n""" % tuple([os.path.basename(selfname)]*4)
		sys.exit(1)

def main(argv):
		if not os.path.isdir(config.wrkdir): os.mkdir(config.wrkdir)
		os.chdir(config.wrkdir)
		quality="hq"
		playargs=[]
		play=False
		offline=False
		offlineplay=False
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
		if "offline" in argv:
				offline=True
				argv.pop(argv.index("offline"))
		if "offlineplay" in argv:
				offlineplay=True
				playindex=argv.index("offlineplay")
				for i in range(playindex, len(argv)):
						playargs.append(argv.pop(playindex))
				playargs.pop(0)

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
				f = open(config.offline_store)
				d = pickle.load(f)
				f.close()
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
						if play_th.is_alive() and mplayer_pid and tmpfilename:
								hangmon(tmpfilename, mplayer_pid)

						if not metadata_fetch_done:
								try:
										metadata, file_base = get_metadata(t_name, quality)
										metadata_fetch_done = True
										quality = metadata["fetched_quality"]
										print "Got metadata" # metadata
								except NoMoreSeries:
										print "No more series"
										sys.exit(0)

						if not sub_fetch_done:
								try:
										if metadata_fetch_done:
												fetch_sub(metadata["subtitles"]["sources"]["en"], file_base+".srt")
												print "Got subtitles"
								except KeyError:
										print "Subtitles not found"
								sub_fetch_done = True

						if not fetch_th.is_alive() and not fetch_done:
								if metadata_fetch_done:
										fetch_th = threading.Thread(target=pfetcher, args=(metadata, file_base,
												quality),
												kwargs={"silent":True, "queue" : fetch_queue})
										fetch_th.daemon = True
										fetch_th.start()
										time.sleep(config.wait_time*10)

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

						if not play_th.is_alive():
								play_th = threading.Thread(target=turboplay.mplay, args=(playargs,),
												kwargs={"latest": file_base+".mp4",
														"queue":play_queue})
								play_th.start()
								print "Playing: \n%s Season %s Episode %s" % (t_name,
										metadata["season"], metadata["number"])
						time.sleep(config.wait_time)

		elif offline:
				offset = 0
				while True:
						metadata, file_base = get_metadata(t_name, quality, offset=offset)
						print "Fetching for offline: \n%s Season %s Episode %s" % (t_name,
								metadata["season"], metadata["number"])
						fetch_sub(metadata["subtitles"]["sources"]["en"], file_base+".srt")
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
						fetch_sub(metadata["subtitles"]["sources"]["en"], file_base+".srt")
						print "Got subtitles"
				except KeyError:
						print "Subtitles not found"
				pfetcher(metadata, file_base, quality)


if __name__ == "__main__":
		main(sys.argv)


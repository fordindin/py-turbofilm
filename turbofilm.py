#!/usr/bin/env python

from xml2srt import fetch_sub
from metaWrapper import get_metadata
import os
import re
import sys
import json
from subprocess import Popen, PIPE
from lastunseen import listunseen
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

				tr = filter(lambda a: a[0]==3, listunseen(retlist=True))
				r = Random()
				t_name = r.choice(tr)[1]

		if len(argv) == 2:
				# obsolete
				#series_data = config.sdata_RE.match(argv[1])
				#if series_data:
				#		t_name, season, number = series_data.groups()
				selfname, t_name = argv

		else: usage(argv[0])



		if play:
				play_th = threading.Thread(target=lambda a: a)
				while True:
						if play_th.is_alive():
								time.sleep(wait_time)
								continue
						else:
								metadata, file_base = get_metadata(t_name, quality)
								quality = metadata["fetched_quality"]
								print "Got metadata" # metadata

								try:
										fetch_sub(metadata["subtitles"]["sources"]["en"], file_base+".srt")
										print "Got subtitles"
								except KeyError:
										print "Subtitles not found"

								pos = 0
								total_fetched_sec = 0
								nprobes = 0
								average = 0
								asize = 0
								queue = Queue.Queue()
								outdata = {}
								wait_time = 1
								fetch_done = False

								fetch_th = threading.Thread(target=pfetcher, args=(metadata, file_base,
										quality),
										kwargs={"silent":True, "outdata":outdata})
								fetch_th.daemon = True
								fetch_th.start()
								logfd = open(file_base+".log", "a+")
								saved_metadata = turboplay.load_saved_meta(file_base+".meta")
								while float(pos)/float(metadata["duration"]) < 0.98 and (fetch_th.isAlive() or
												fetch_done):
										total = average*nprobes
										if not os.path.isfile(file_base+".mp4"):
												bsize = 0
										else:
												bsize = os.stat(file_base+".mp4").st_size

										if not fetch_done: time.sleep(wait_time)
										asize = os.stat(file_base+".mp4").st_size
										if asize == bsize and fetch_th.isAlive(): continue
										if bsize >= float(metadata["sizes"][quality]):
												fetch_done = True
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
																kwargs={"latest": file_base+".mp4", "queue":queue})
												play_th.start()
												#play_th.join()
												if not queue.empty():
														pos = queue.get()
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


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
import metaWrapper
import config
from functions import hangmon

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
		if not os.path.isdir(os.path.join(config.wrkdir,t_name)): os.mkdir(os.path.join(config.wrkdir,t_name))

		play_th = threading.Thread(target=lambda a: a)
		play_queue = Queue.Queue()
		fetch_queue = Queue.Queue()
		tmp_queue = Queue.Queue()
		pid_queue = Queue.Queue()
		mplayer_pid = None


		if play:
				while True:
						if play_th.is_alive():
								hangmon(tmpfilename, mplayer_pid)
								time.sleep(config.wait_time)
								continue
						else:

								#if "fetch_done" not in locals().keys(): fetch_done = False
								fetch_done = False

								if not fetch_done:
										metadata, file_base = get_metadata(t_name, quality)
										quality = metadata["fetched_quality"]
										print "Got metadata" # metadata

										try:
												fetch_sub(metadata["subtitles"]["sources"]["en"], file_base+".srt")
												print "Got subtitles"
										except KeyError:
												print "Subtitles not found"

										pos = nprobes = average = asize = 0
										tmpfilename = None

										fetch_th = threading.Thread(target=pfetcher, args=(metadata, file_base,
												quality),
												kwargs={"silent":True, "queue" : fetch_queue})
										fetch_th.daemon = True
										fetch_th.start()
										# give fetch thread a second
										time.sleep(config.wait_time)

										if not fetch_queue.empty():
												fetch_done = fetch_queue.get()

										while float(pos)/float(metadata["duration"]) < 0.98 and (fetch_th.is_alive() or fetch_done):
												total = average*nprobes
												hangmon(tmpfilename, mplayer_pid)
												if not os.path.isfile(file_base+".mp4"):
														bsize = 0
														# create empty file
														open(file_base+".mp4","a").close()
												else:
														bsize = os.stat(file_base+".mp4").st_size
												#asize = os.stat(file_base+".mp4").st_size
												if asize == bsize and fetch_th.is_alive(): continue
												if bsize >= float(metadata["sizes"][quality]):
														fetch_done = True
												fetch_per_sec = float(asize-bsize)/float(metadata["bitrate"])/config.wait_time
												fetched_secs = float(bsize)/float(metadata["bitrate"])
												nprobes+=1
												"""
												if nprobes % 15 == 0 and not fetch_done:
														print >> logfd, "%s : total time fetched: %s" % (
																time.strftime("%H:%M %d-%m-%Y"), total)
														print >> logfd, "%s : average fetch speed (sps): %s" % (
																time.strftime("%H:%M %d-%m-%Y"), average)
														print >> logfd, "%s : last period fetch speed (sps): %s" % (
																time.strftime("%H:%M %d-%m-%Y"), fetch_per_sec)
														print >> logfd, "%s : last period fetch speed (kbps): %s" % (
																time.strftime("%H:%M %d-%m-%Y"), float(asize-bsize)/config.wait_time/1024)
														print >> logfd, "%s : total size (kbps): %s" % (
																time.strftime("%H:%M %d-%m-%Y"), asize/1024)
														if saved_metadata.has_key("lastpos"):
																print >> logfd, "%s : last position (kb): %s" % (
																		time.strftime("%H:%M %d-%m-%Y"),
																		saved_metadata["lastpos"]*metadata["bitrate"]/1024)
														logfd.flush()
												"""
												average = (total+fetch_per_sec)/nprobes

												if not fetch_queue.empty():
														fetch_done = fetch_queue.get()

												if not play_queue.empty():
														pos = play_queue.get()

												if (not total and not fetch_done) or \
													 (float(pos)/float(metadata["duration"]) >= 0.98):
															 continue

												if ( ( ( average > 3 and nprobes > 3) or fetch_done ) \
																or float(fetched_secs)-float(pos) > 10*average ) \
																and not play_th.is_alive(): # and \
														play_th = threading.Thread(target=turboplay.mplay, args=(playargs,),
																		kwargs={"latest": file_base+".mp4",
																				"queue":play_queue, "tmpqueue":tmp_queue,
																				"pidqueue":pid_queue})
														print "Playing: \n%s Season %s Episode %s" % (t_name,
																metadata["season"], metadata["number"])
														if not os.path.isfile(file_base+".mp4"):
																open(file_base+".mp4","a").close()
														play_th.start()
														#play_th.join()
														# wait until tmp_queue will be filled with tmpfile value
														while tmp_queue.empty():
																time.sleep(config.wait_time)
														tmpfilename = tmp_queue.get()

														if not play_queue.empty():
																pos = play_queue.get()
														if not pid_queue.empty():
																mplayer_pid = int(pid_queue.get())

														if float(pos)/float(metadata["duration"]) >= 0.98:
																fetch_done = False
												else: time.sleep(config.wait_time)
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


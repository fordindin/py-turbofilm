#!/usr/bin/env python

import sys
import functions
import lastunseen

def viewmap():
		for snu in  lastunseen.listunseen(retlist=True):

				slist = functions.getSeasons(snu[1])
				s = slist.keys()
				s.sort()
				ssn = lastunseen.lastunseen_ssn(snu[1])
				sys.stdout.write("% 30s  " %  ssn[0])
				for k in s:
						sys.stdout.write("|")
						for e in slist[k]:
								if slist[k].index(e) == ssn[2]-1 and ssn[1] == k:
										sys.stdout.write("+")
								else:
										sys.stdout.write("_")
				sys.stdout.write("|")
				sys.stdout.write("\n")

def listunseen():
		for snu in  lastunseen.listunseen(retlist=True):
				unseen = 0
				# names of episodes grouped by seasons {numOfSeason: [list, of, names]}
				slist = functions.getSeasons(snu[1])

				#nseasosns = s[-1]

				# last watched [ SeriesName, lastWatchedSeason, lastWatchedEpisode ]
				ssn = lastunseen.lastunseen_ssn(snu[1])

				for k,v in slist.items():
						if k < ssn[1]:
								pass
						elif k == ssn[1]:
								unseen += len(v) - ssn[2] + 1
						elif k > ssn[1]:
								unseen += len(v)

				print "% 20s\t% 3d" % (ssn[0], unseen)



#!/usr/bin/env python

import os
import re
import config
from GetPage import getpage
from MyHTMLParser import GetNSeasons, GetSeriesDescription
from urllib import basejoin as urljoin

def hangmon(tmpfilename, mplayer_pid):
		if tmpfilename and os.path.exists(tmpfilename):
				try: 
						os.kill(mplayer_pid, 0)
				except OSError:
						return None
				offset = os.stat(tmpfilename).st_size - 150
				tmpfile = open(tmpfilename, "r")
				tmpfile.seek(offset)
				d = tmpfile.read()
				tmatch = re.match(".*A-V:\s*([0-9\-\.]+).*", d)
				#if tmatch: print float(tmatch.groups()[0])
				if tmatch and float(tmatch.groups()[0]) > 0.5 and mplayer_pid:
						print "\nMplayer seems stuck. Killing mplayer"
						#print "diff: %s" % tmatch.groups()[0]
						os.kill(mplayer_pid, 15)

def debug(fmt, *argc):
		if config.debug:
				print fmt % argc >> os.stderr

def getSeasons(sname):
		url = urljoin(config.turbofilm_base,os.path.join("Series",sname))
		parser = GetNSeasons()
		page = getpage(url)["page"]
		parser.feed(page)
		slinks = parser.get_slinks()
		seasons = {}
		for s in slinks:
				k = int(re.match(".*([0-9]+)$", s).groups()[0])
				seasons.setdefault(k)
				u = urljoin(config.turbofilm_base, s)
				pg = getpage(u)["page"]
				p = GetSeriesDescription()
				p.feed(pg)
				seasons[k] = p.get_names()
		return seasons

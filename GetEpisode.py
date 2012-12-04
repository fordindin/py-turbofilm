#!/usr/bin/env python

import GetPage
from xml.dom.minidom import parseString
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
from subprocess import Popen, PIPE, STDOUT

wrkdir = "/Users/dindin/tmp/turbofilm"
maxretry = 5

class MyHTMLParser(HTMLParser):
		metadata=None
		def handle_starttag(self, tag, attrs):
				if ("id", "metadata") in attrs:
						for a in attrs:
								if a[0] == 'value':
										self.metadata=a[1]

quality="hq"
argv = sys.argv
if "-lq" in argv:
		quality = "default"
		argv.pop(argv.index("-lq"))

series_data = re.match("http://turbofilm.tv/Watch/(.*)/Season(.*)/Episode(.*)",sys.argv[1])
if series_data:
		t_name, season, number = series_data.groups()
else:
		selfname, t_name, season, number = argv


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

sts = 1
trycount = 0

while sts != 0:
		print "Try number %d" % trycount
		p = Popen(
						["/opt/local/bin/wget",
				"-c", "-O", dir_name+".mp4",
				cdn_url(iasid,
						metadata["eid"],
						metadata["sources2"][quality],
						0,
						"en")
				],
		)
		#retcode = os.execv(
		#		)["subtitles"]["sources"]["en"
		pid, sts = os.waitpid(p.pid, 0)
		trycount += 1
		if trycount > maxretry: break


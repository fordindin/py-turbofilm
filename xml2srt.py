#!/usr/bin/env python
# coding: utf-8

import sys, os, time
import math
import urllib2
import xml.dom.minidom
import config

def sec_format(strsec):
		fsec = float(strsec.replace(",","."))
		hours = int(fsec) / (60**2)
		minutes = int(fsec - hours*(60**2)) / (60**1)
		seconds = fsec-(hours*(60**2)+minutes*(60**1))
		flt = float(fsec) - math.floor(fsec)
		retstr =  "%02d:%02d:%02d,%d" % (hours, minutes,
						seconds,int(flt*1000))
		return unicode(retstr)

def main(argv):
		infile = argv[1]
		srt_match = config.srt_urlRE.match(infile)
		if srt_match:
				infile = config.sub_base + srt_match.groups()[0]
		fetch_sub(infile)

def fetch_sub(infile, srt_location="/Users/dindin/tmp/lastflash.srt"):
		if not config.proto_RE.match(infile):
				infile = config.proto + infile
		#print infile
		f = urllib2.urlopen(infile)
		srt = file(srt_location, "w")
		counter = 0

		data = unicode(f.read(), errors='ignore') #.decode("utf-8-sig").strip()
		#print type(data)
		dom = xml.dom.minidom.parseString(data)
		for e in dom.getElementsByTagName("subtitle"):
				data = ""
				try: 
						e.getElementsByTagName("start")[0].childNodes[0].data
						counter+=1
						data+=u"%s\n" % (counter)
						data+=u"%s --> %s\n" % (
							sec_format(e.getElementsByTagName("start")[0].childNodes[0].data),
							sec_format(e.getElementsByTagName("end")[0].childNodes[0].data))
						data+="%s\n\n" % e.getElementsByTagName("text")[0].childNodes[0].data
						srt.write(data)
				except IndexError: pass
		srt.close()

if __name__ == '__main__':
		sys.exit(main(sys.argv))

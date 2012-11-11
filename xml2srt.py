#!/usr/bin/env python

import re, sys, os, time
import math
import urllib2

srt_urlRE='http://(?:.*)/([0-9a-f]{32}).*'

sub_base="http://sub.turbofilm.tv/en/"
bs_RE = ".*<subtitle>.*"
be_RE = ".*</subtitle>.*"
start_RE = "<start>([0-9,.]*)</start>"
stop_RE = "<end>([0-9,.]*)</end>"
text_RE = "<text>(.*)</text>"



def sec_format(strsec):
    fsec = float(strsec.replace(",","."))
    hours = int(fsec) / (60**2)
    minutes = int(fsec - hours*(60**2)) / (60**1)
    seconds = fsec-(hours*(60**2)+minutes*(60**1))
    flt = float(fsec) - math.floor(fsec)
    retstr =  "%02d:%02d:%02d,%d" % (hours, minutes,
            seconds,int(flt*1000))
    return retstr



def main(argv):
    infile = argv[1]
    srt_match = re.match(srt_urlRE, infile)

    if srt_match:
        infile=sub_base + srt_match.groups()[0]
    fetch_sub(infile)


def fetch_sub(infile, srt_location="/Users/dindin/tmp/lastflash.srt"):
    print infile
    f = urllib2.urlopen(infile)
    srt = file(srt_location, "w")
    line = True
    counter = 0
    while line:
      line = f.readline()
      if re.match(bs_RE,line):
          counter += 1
          block = "" 
          while not re.match(be_RE,line):
              line = f.readline()
              block += line.replace('\n',' ')
              block = block.replace('\r', '')
          start = re.findall(start_RE,block)[0]
          stop = re.findall(stop_RE,block)[0]
          try:
              text = re.findall(text_RE,block)[0]
              text = text.replace("&lt;i&gt;", "<i>")
              text = text.replace("&lt;/i&gt;", "</i>")
          except IndexError: continue

          srt.write("%s\n" % (counter))
          srt.write("%s --> %s\n" % (sec_format(start), sec_format(stop)))
          srt.write("%s\n\n" % text.replace("\r ","\n"))
    srt.close()

if __name__ == '__main__':
    sys.exit(main(sys.argv))

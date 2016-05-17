#!/usr/bin/env python

from metaWrapper import unwatchEpisode
import sys,json

eid = json.load(sys.argv[1])["eid"]

unwatchEpisode(eid)

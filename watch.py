#!/usr/bin/env python

from metaWrapper import watchEpisode
import sys,json

eid = json.load(open(sys.argv[1]))["eid"]

watchEpisode(eid)

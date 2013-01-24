#!/usr/bin/env python

import GetPage
import config

def watchEpisode(eid):
				postdata = { "watch": 1, "eid": eid }
				return GetPage.getpage(config.watchUrl, postdata)

def unwatchEpisode(eid):
				postdata = { "watch": 0, "eid": eid }
				return GetPage.getpage(config.watchUrl, postdata)

if __name__ == '__main__':
		eid = 5669
		print watchEpisode(eid)
		print unwatchEpisode(eid)

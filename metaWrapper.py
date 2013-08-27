#!/usr/bin/env python

import os
from urllib2 import unquote
import json
import config
import GetPage
from MyHTMLParser import MetaHTMLParser
from lastunseen import get_series_ssn
from cdn_url import ssn_url
from wierd_b64_decode import w_base64_decode as wb64
import xml2obj

def get_metadata(t_name, quality, offset=0):
		t_name, season, number = get_series_ssn(t_name, offset=offset)
		fname_base = "S%02dE%02d" % (int(season), int(number))

		file_base = os.path.join(config.wrkdir, t_name, fname_base)
		parser = MetaHTMLParser()
		page = GetPage.getpage(ssn_url(t_name, season, number))["page"]
		iasid = GetPage.p.check_ssid()
		parser.feed(page)
		xml_metadata = wb64(unquote(parser.metadata))
		#print "Got XML" # xml_metadata


		metadata = xml2obj.xml2obj(xml_metadata)
		metadata["fetched_quality"] = quality
		if metadata["sizes"]["hq"] == "0":
				metadata["fetched_quality"] = "default"
				quality = "default"
		metadata["iasid"] = iasid
		metadata["season"] = season
		metadata["number"] = number

		if not os.path.isfile(file_base+".meta") or os.stat(file_base+".meta").st_size == 0:
				fd = open(file_base+".meta", "w")
				fd.write(json.dumps(metadata))
				fd.close()
		metadata.update({'bitrate': float(metadata["sizes"][quality])/float(metadata['duration'])})
		#print "bitrate: %s byte/sec" % metadata['bitrate']
		return metadata, file_base

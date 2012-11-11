#!/usr/bin/env python

from hashlib import sha1
from random import random

def cdn_url(iasid, eid, current_source, offset, lang):
		print lang, offset, current_source
		rseed = sha1(iasid + str(random())).hexdigest()
		skey = sha1(rseed + eid + "A2DC51DE0F8BC1E9").hexdigest()
		return "http://cdn.turbofilm.tv/"+ sha1(lang).hexdigest() + "/" + \
						eid + "/" +\
						current_source + "/" +\
						str(offset) + "/" +\
						iasid + "/" +\
						rseed + "/" +\
						skey + "/r"

"""
						09071f9d3a192bb6120274c473e9b65c8373df49
						{'sizes': {'default': '224719185', 'hq': '128446464'}, 'duration': '2560',
						'eid': '6638', 'aspect': '169', 'sources2': {'default':
						'df9980154cedb1ac12b2954db63c06d4', 'hq': '048433c326bdb8a4ef61ca2bd8b5c854'},
						'subtitles': {'sources': {'ru':
						'http://sub.turbofilm.tv/ru/9f0cdecf51e7c2bdfdcac1dc781e70ae', 'en':
						'http://sub.turbofilm.tv/en/9f0cdecf51e7c2bdfdcac1dc781e70ae'}}}"""

# playWrapper(currentSource, Math.round(a * (metadata.duration / SEEKBAR_WIDTH)), currentLang);



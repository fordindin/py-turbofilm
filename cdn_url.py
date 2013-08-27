#!/usr/bin/env python

from hashlib import sha1
from random import random
import config

def ssn_url(t_name, season, episode):
		return config.sdata_TMPL % (config.proto, t_name, season, episode)

def cdn_url(iasid, eid, current_source, offset, lang):
		rseed = sha1(iasid + str(random())).hexdigest()
		skey = sha1(rseed + eid + config.cdn_authkey).hexdigest()
		return "/".join([
				config.cdn_base_uri,
				sha1(lang).hexdigest(),
				eid,
				current_source,
				str(offset),
				iasid,
				rseed,
				skey,
				"r",
				])

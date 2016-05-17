#!/usr/bin/env python

import urllib, urllib2, cookielib, getpass
#from xml.etree.ElementTree import ElementTree
#import StringIO
#import xml.dom.minidom
#import os, re, time

from TurboAuth import TurboAuth
import config
import ssl


p = TurboAuth(config.login)

def auth(login):
	if not p.check_ssid():
			p.set_password(getpass.getpass("password for %s:" % config.login))
			p.get_cookies()

def getpage(url, data={}, headers={}):
	data = urllib.urlencode(data)
	auth(config.login)
	#req = urllib2.urlopen(url)
	req = urllib2.Request(url, data, headers)
	response = urllib2.urlopen(req)
	return {"page": response.read()}

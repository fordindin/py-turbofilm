#!/usr/bin/env python

import urllib, urllib2, cookielib, getpass
#from xml.etree.ElementTree import ElementTree
#import StringIO
#import xml.dom.minidom
#import os, re, time

from TurboAuth import PassportAuth

p = PassportAuth()
login = "dindin@dindin.ru"

def auth(login):
	if not p.check_ssid():
			p.get_cookies(login, getpass.getpass("password for %s:" % login))

def getpage(url, data={}, headers={}):
	data = urllib.urlencode(data)
	auth(login)
	req = urllib2.urlopen(url)
	req = urllib2.Request(url, data, headers)
	response = urllib2.urlopen(req)
	return {"page": response.read()}

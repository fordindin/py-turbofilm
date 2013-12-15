#!/usr/bin/env python
# coding: utf-8

import urllib, urllib2, cookielib
import httplib
import os, re, time
import config
import socket
import socks
import ssl
import dns.resolver
import sys

from socksipyhandler import SocksiPyHandler

""" This module emulates Turbofilm.tv auth.
It checks cookies in given cookie jar, and put there
valid cookies in case of expiration"""


dns.resolver.override_system_resolver( dns.resolver.Resolver(filename='resolv.conf') )
cj = config.cookie_path

class TurboAuth:
		def __init__(self, login, password=None):
				self.cookie_jar = cookielib.LWPCookieJar(filename=cj)
				if os.path.isfile(cj): self.cookie_jar.load(cj)
				# clear expired and session cookies
				self.cookie_jar.clear_expired_cookies()
				self.cookie_jar.clear_session_cookies()
				# install cookies
				openers_list = []
				if config.socks_enable:
						openers_list.append(
								SocksiPyHandler(socks.PROXY_TYPE_SOCKS4,
								config.socks_ip, config.socks_port))
				openers_list.append(urllib2.HTTPCookieProcessor(self.cookie_jar))
				opener=urllib2.build_opener(*openers_list)
				urllib2.install_opener(opener)
				self.login = login
				self.set_password(password)

		def check_ssid(self):
				for e in self.cookie_jar:
						if e.name == "IAS_ID":
								return e.value
				return False

		def set_password(self, password):
				self.password = password

		def get_cookies(self):
				req = urllib2.urlopen(config.auth_url)
				datadict = {
						"login": self.login,
						"passwd": self.password,
						"remember": "on",
				}
				data = urllib.urlencode(datadict)
				req = urllib2.Request(config.auth_url, data, config.headers)
				response = urllib2.urlopen(req)
				the_page = response.read()
				self.cookie_jar.save(cj)
				return True

		@classmethod
		def clear_cookies(obj):
				os.remove(cj)
				return True


if __name__ == '__main__':
		import getpass
		__doc__ = """ checking cookie operations."""
		print __doc__
		login = "dindin@dindin.ru"
		password = getpass.getpass("password for %s:" % login)
		p = TurboAuth(user, password)
		print p.get_cookies(), p.cookie_jar, p.check_ssid()

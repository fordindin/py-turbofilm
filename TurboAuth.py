#!/usr/bin/env python
# coding: utf-8

import urllib, urllib2, cookielib
#from xml.etree.ElementTree import ElementTree
#import StringIO
#import xml.dom.minidom
import os, re, time

""" This module emulates Yandex.Passport auth.
It checks cookies in given cookie jar, and put there
valid cookies in case of expiration"""

passport_auth_url="http://turbofilm.tv/Signin"
headers =  { 'User-Agent' : "Mozilla/5.0 compatible pure-python Turbofilm.tv client" }
cj=os.path.expanduser("~/.turbofilm.tv.cookie")

class PassportAuth:
    def __init__(self):
        self.cookie_jar = cookielib.LWPCookieJar(filename=cj)
        if os.path.isfile(cj): self.cookie_jar.load(cj)

        # clear expired and session cookies
        self.cookie_jar.clear_expired_cookies()
        self.cookie_jar.clear_session_cookies()

        # install cookies
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        urllib2.install_opener(opener)

    def check_ssid(self):
      for e in self.cookie_jar:
        if e.name == "IAS_ID":
          return e.value
      return False

    def get_cookies(self, username, password):
        # get idkey, it's seems not nessesary, but we'll do it for
        # sure
        req = urllib2.urlopen(passport_auth_url)
        #try:
        #    idkey = idkey_RE.findall(req.read())[0]
        #except IndexError: idkey = None

        # yandex.Passport auth data
        datadict = {
                    "login": username,
                    "passwd": password,
		    "remember": "on",
                    }
        data = urllib.urlencode(datadict)

        # get Session_id cookie from yandex.Passport 
        req = urllib2.Request(passport_auth_url, data, headers)
        response = urllib2.urlopen(req)
        the_page = response.read()
        self.cookie_jar.save(cj)
        return True

    @classmethod
    def clear_cookies(obj):
        os.remove(cj)
        return True


if __name__ == '__main__':
    __doc__ = """ checking cookie operations.
True"""
    print __doc__
    import getpass
    p = PassportAuth()
    #login=getpass.getuser()
    login = "dindin@dindin.ru"
    password = getpass.getpass("password for %s:" % login)
    print p.get_cookies(login, password)
    print p.cookie_jar
    print p.check_ssid()
    #print p.clear_cookies()
    

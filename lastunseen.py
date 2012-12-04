#!/usr/bin/env python

import GetPage
from HTMLParser import HTMLParser
import re

class MyHTMLParser(HTMLParser):
		tstack = []
		unseen = []
		def handle_starttag(self, tag, attrs):
				self.tstack.append((tag,attrs))
				if tag == 'a' and self.tstack[-2][1][0][1] == 'myseriesbox':
						self.unseen.append(attrs[0][1])
		def handle_endtag(self, tag):
				self.tstack.pop()
		def handle_startendtag(self, tag, attrs):
				pass
		def get_unseen(self):
				return self.unseen

def lastunseen(seriesName):
	parser = MyHTMLParser()
	page = GetPage.getpage('http://turbofilm.tv/My/Series')["page"]
	parser.feed(page)
	for u in parser.get_unseen():
			if re.match('.*\/%s\/.*' % seriesName, u):
					return 'http://turbofilm.tv' + u

def listunseen():
	unseen = {}
	unseen_list = []
	retstr = ""
	parser = MyHTMLParser()
	page = GetPage.getpage('http://turbofilm.tv/My/Series')["page"]
	parser.feed(page)
	for u in parser.get_unseen():
			series = re.match('/Watch/(.*)/Season', u).groups()[0]
			if series:
					unseen.setdefault(series, [])
					unseen[series].append(u)
	for k in unseen.keys():
			unseen_list.append((len(unseen[k]), k))
			def comp(a,b):
					if a[0] > b[0]: return 1
					elif a[0] < b[0]: return -1
					else: return 0
			unseen_list.sort(cmp=comp)
	for e in unseen_list:
			if e[0] == 3: 
					prefix = ">="
			else: prefix = "=="
			retstr+=prefix+" %d\t%s\n" % e
	return retstr

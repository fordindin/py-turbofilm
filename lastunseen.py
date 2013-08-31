#!/usr/bin/env python

import GetPage
from MyHTMLParser import UnseenHTMLParser
import re
import config


def get_series_ssn(t_name, offset=0):
		url = lastunseen(t_name)
		series_data = config.sdata_RE.match(url)
		t_name, season, number = series_data.groups()
		print t_name, season, number
		number = int(number) + offset
		return t_name, season, number

def lastunseen(seriesName):
	parser = UnseenHTMLParser()
	page = GetPage.getpage(config.series_page)["page"]
	parser.feed(page)
	for u in parser.get_unseen():
			if re.match('.*\/%s\/.*' % seriesName, u):
					print config.turbofilm_base + u
					return config.turbofilm_base + u

def listunseen(retlist=False):
	unseen = {}
	unseen_list = []
	retstr = "\n"
	parser = UnseenHTMLParser()
	page = GetPage.getpage(config.series_page)["page"]
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
	if retlist: return unseen_list
	for e in unseen_list:
			if e[0] == 3: 
					prefix = ">="
			else: prefix = "=="
			retstr+=prefix+" %d\t%s\n" % e
	retstr += "\n"+"-"*20 + "\n\t%s\n" % parser.get_unseen_text()
	return retstr

if __name__ == '__main__':
		pass


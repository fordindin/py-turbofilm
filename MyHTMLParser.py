#!/usr/bin/env python

from HTMLParser import HTMLParser

class MetaHTMLParser(HTMLParser):
		def __init__(self):
				HTMLParser.__init__(self)
				metadata = None
		def handle_starttag(self, tag, attrs):
				if ("id", "metadata") in attrs:
						for a in attrs:
								if a[0] == 'value':
										self.metadata=a[1]

class UnseenHTMLParser(HTMLParser):
		def __init__(self):
				HTMLParser.__init__(self)
				self.tstack = []
				self.unseen = []
				self.unseen_text = ""
				self.epcounthead_opened = False
		def handle_starttag(self, tag, attrs):
				self.tstack.append((tag,attrs))
				if tag == 'a' and self.tstack[-2][1][0][1] == 'myseriesbox':
						self.unseen.append(attrs[0][1])
				if tag == 'span' and ('id', 'epcounthead') in attrs:
						self.epcounthead_opened = True
		def handle_endtag(self, tag):
				if self.epcounthead_opened:
						self.epcounthead_opened = False
				self.tstack.pop()
		def handle_startendtag(self, tag, attrs):
				pass
		def handle_data(self, data):
				if self.epcounthead_opened:
						self.unseen_text =  data
		def get_unseen(self):
				return self.unseen
		def get_unseen_text(self):
				return self.unseen_text

class GetNSeasons(HTMLParser):
		def __init__(self):
				self.mfound = False
				self.slinks = []
				HTMLParser.__init__(self)
		def handle_starttag(self, tag, attrs):
				#if tag == 'div': print attrs
				if tag == 'div' and "class" ==  attrs[0][0] and attrs[0][1] == "seasonnum":
						self.mfound = True
				if self.mfound and tag == "a":
						self.slinks.append(attrs[0][1])
		def handle_endtag(self, tag):
				if tag == 'div' and self.mfound:
						self.mfound=False
				pass
		def handle_startendtag(self, tag, attrs):
				pass
		def get_slinks(self):
				return self.slinks

class GetSeriesDescription(HTMLParser):
		def __init__(self):
				HTMLParser.__init__(self)
				self.dfound = None
				self.nfound = False
				self.names = []
		def handle_starttag(self, tag, attrs):
				if tag == 'span' and attrs[0] == ("class","sserieslistonetxt"):
						self.dfound = True
				if self.dfound and tag == 'span' and attrs[0] == ("class","sserieslistonetxten"):
						self.nfound = True
		def handle_endtag(self, tag):
				if self.dfound and tag == 'span':
						self.dfound == False
				if self.nfound and tag == 'span':
						self.nfound = False
				pass
		def handle_startendtag(self, tag, attrs):
				pass
		def handle_data(self, data):
				if self.nfound:
						self.names.append(data)
		def get_names(self):
				return self.names

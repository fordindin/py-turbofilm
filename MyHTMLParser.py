#!/usr/bin/env python

from HTMLParser import HTMLParser

class MetaHTMLParser(HTMLParser):
		metadata = None
		def handle_starttag(self, tag, attrs):
				if ("id", "metadata") in attrs:
						for a in attrs:
								if a[0] == 'value':
										self.metadata=a[1]

class UnseenHTMLParser(HTMLParser):
		tstack = []
		unseen = []
		unseen_text = ""
		epcounthead_opened = False
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

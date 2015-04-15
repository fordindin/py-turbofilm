#!/usr/bin/env python

import lastunseen

last = lastunseen.lastunseen("OrangeIsTheNewBlack")


class AllUnseenHTMLParser(HTMLParser):
		def __init__(self):
				HTMLParser.__init__(self)
				self.tstack = []
		def handle_starttag(self, tag, attrs):
				self.tstack.append((tag,attrs))
				if tag == 'div' and ('id', 'eplist') in attrs:
						print tag, attrs





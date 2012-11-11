#!/usr/bin/env python

from xml.etree.ElementTree import fromstring

def xml2obj(indata):
		outobj = {}
		xml = fromstring(indata.replace("utf-16","utf-8"))
		outobj["sources2"]={}
		try:
				outobj["sources2"]["default"] = xml.find("sources2/default").text
		except AttributeError: pass
		outobj["sources2"]["hq"] = xml.find("sources2/hq").text

		outobj["sizes"]={}
		try:
				outobj["sizes"]["default"] = xml.find("sizes/default").text
		except AttributeError: pass
		outobj["sizes"]["hq"] = xml.find("sizes/hq").text

		outobj["subtitles"] = {}
		outobj["subtitles"]["sources"] = {}
		try:
				outobj["subtitles"]["sources"]["en"] = xml.find("subtitles/sources/en").text
		except AttributeError: pass
		try:
				outobj["subtitles"]["sources"]["ru"] = xml.find("subtitles/sources/ru").text
		except AttributeError: pass

		outobj["aspect"] = xml.find("aspect").text
		outobj["duration"] = xml.find("duration").text
		outobj["eid"] = xml.find("eid").text
		return outobj

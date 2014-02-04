#!/usr/bin/env python
# coding: utf-8

import re
import os

proto = "https:"


turbofilm_base = 'https://turbik.tv'

proto_RE = re.compile("(http:|ftp:|https).*")

srt_urlRE=re.compile('https://(?:.*)/([0-9a-f]{32}).*')

sub_base="http://sub.turbik.tv/en/"

login = "dindin@dindin.ru"

auth_url="https://turbik.tv/Signin"

headers =  { 'User-Agent' : "Mozilla/5.0 compatible pure-python Turbofilm.tv client" }

cookie_path = os.path.expanduser("~/.turbik.tv.cookie")

cdn_base_uri = "https://cdn.turbik.tv/"
cdn_authkey = "A2DC51DE0F8BC1E9"

max_fetch_retry = 5

wait_time = 1

series_page = "https://turbik.tv/My/Series"

watchUrl = 'https://turbik.tv/services/epwatch'

sdata_RE = re.compile("http(?:s)+://turbik.tv/Watch/(.*)/Season(.*)/Episode(.*)")
sdata_TMPL = "%s//turbik.tv/Watch/%s/Season%s/Episode%s"

wrkdir = "%s/turbofilm" % os.getenv("HOME")

offline_dir = os.path.join(wrkdir, "offline")

socks_enable = False
socks_ip = "199.231.185.97"
socks_port = 1080
#socks_ip = "127.0.0.1"
#socks_port = 9050
#myresolver="resolv.conf"
myresolver=False

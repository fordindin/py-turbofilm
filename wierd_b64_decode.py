#!/usr/bin/env python

from base64 import b64decode

def enc_replace_ab(e, d, s):
		s = s.replace(e, "___")
		s = s.replace(d, e)
		s = s.replace("___",d)
		return s

def enc_replace(g, f):
		a = 0
		e = "2I0=3Q8V7XGMRUH41Z5DN6L9BW"
		d = "xuYokngrmTwfdcesilytpbzaJv"
		c = d
		b = e
		while a < len(c):
				g = enc_replace_ab(c[a], b[a], g)
				a+=1
		return g

def w_base64_decode(a):
    a = enc_replace(a, "d")
    return b64decode(a)

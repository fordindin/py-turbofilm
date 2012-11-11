#!/usr/bin/env python

from base64 import b64decode

"""
BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
def decodeToByteArray(g):
		b = ""
		e = [None, None, None, None]
		d = [None, None, None]
		for f in range(0,len(g), 4):
				for c in range(0,4):
						if f+c >= len(g): break
						e[c] = BASE64_CHARS.index(g[f+c])
				d[0] = (e[0] << 2) | (e[1] >> 4)
				d[1] = ((e[1] & 15) << 4) | (e[2] >> 2)
				d[2] = ((e[2] & 3) << 6) | e[3]
				for a in range(len(d)):
						if e[a+1] == 64: break
						b+=chr(d[a])
		return b
"""

def enc_replace_ab(e, d, s):
		s = s.replace(e, "___")
		s = s.replace(d, e)
		s = s.replace("___",d)
		return s

def enc_replace(g, f):
		a=0
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
    #return decodeToByteArray(a)
    return b64decode(a)

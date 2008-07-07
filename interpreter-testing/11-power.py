#!/usr/bin/python

def power(b,e):
	if e == 1:
		return b
	else:
		return b * power(b, e-1)

power(5, 3)

#!/usr/bin/python

x = 42 - 19      # x = 23
y = not x        # y = False
z = not (x - 23) # z = True

x and y and z    # => 23 ('and' returns its last non-false argument)

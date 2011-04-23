#!/usr/bin/env python

'''
Created on 15/04/2011

@author: yang
'''

class BdeErrorLog(object):

        
    def __init__(self):
        self.errorList = []
        
    def add(self, code, line):
        self.errorList.append((code, line))
        
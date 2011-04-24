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
        
        
class BdeException(Exception):
    
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
        
        
    
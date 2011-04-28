#!/usr/bin/env python

'''
Created on 15/04/2011

@author: yang
'''

class BdeErrorLog(object):

    def __init__(self):
        self.list = []
        
    def add(self, code, line):
        self.list.append((code, line))
        
    def show(self):
        for error in self.list:
            print error[0], ': ', error[1].getLineNumber()
        
        
class BdeException(Exception):
    
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
        
        
    
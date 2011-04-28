#!/usr/bin/env python

import errorcode

'''
Created on 15/04/2011

@author: yang
'''

class BdeErrorLog(object):

    def __init__(self):
        self.errordict = {}
        
    def add(self, code, lineNumber):
        self.errordict[code] = lineNumber
        
    def show(self, bdefileobj, verbose=False):
        keys = self.errordict.keys()
        keys.sort()
        for key in keys:
            print 'Error %d: %s (%d lines)' % (key, errorcode.getDescription(key), len(self.errordict[key]))
            if verbose:
                for idx in self.errordict[key]:
                    line = bdefileobj.getLine(idx)
                    print '    %s' % line
        
    def hasError(self):
        if len(self.errordict) > 0:
            return True
        else:
            return False
        
        
class BdeException(Exception):
    
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)
        
        
    
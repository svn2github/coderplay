#!/usr/bin/env python

'''
Created on 15/04/2011

@author: yang
'''

class BdeSumup(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.lines = []
        
        
    def addLine(self, line):
        self.lines.append(line); 
        
        
    def calculateDuration(self):
        '''
        Calculate the duration of the sumup by take the time difference of
        the first line and the last line. Duration unit is hour.
        '''
        stime = self.lines[0].getDateTime()
        etime = self.lines[len(self.lines)-1].getDateTime()
        return (etime-stime).seconds/3600.

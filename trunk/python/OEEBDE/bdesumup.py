#!/usr/bin/env python

'''
Created on 15/04/2011

@author: yang
'''

class BdeSumup(object):
    '''
    classdocs
    '''

    def __init__(self, name):
        '''
        Constructor
        '''
        self.name = name
        self.lines = []
        self.status = 0
        
        
    def addLine(self, line):
        self.lines.append(line);
    
    def getFirstLine(self):
        return self.lines[0]
        
    def getLastLine(self):
        return self.lines[len(self.lines)-1]
        
    def getStartTime(self):
        return self.getFirstLine().getDateTime()
        
    def getEndTime(self):
        return self.getLastLine().getDateTime()
        
    def calculateDuration(self):
        '''
        Calculate the duration of the sumup by take the time difference of
        the first line and the last line. Duration unit is hour.
        '''
        stime = self.getStartTime()
        etime = self.getEndTime()
        return (etime-stime).seconds/3600.
        
    def calculateImpressionTotal(self):
        sit = self.getFirstLine().getImpressionTotal()
        eit = self.getLastLine().getImpressionTotal()
        return eit-sit


class BdeSumupList(object):
    
    def __init__(self):
        self.list = []
        
    def add(self, sumup):
        # Add the sumup in order of start time
        stime = sumup.lines[0].getDateTime()
        if self.list == []:
            self.list.append(sumup)
        else:
            for idx, element in enumerate(self.list):
                if element.lines[0].getDateTime() > stime:
                    self.list.insert(idx, sumup)
                    return
            self.list.append(sumup)
                    
                    
    def __iter__(self):
        return iter(self.list)
    
        
        
        
        
        
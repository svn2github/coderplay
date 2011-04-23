#!/usr/bin/env python

import csv
import datetime

'''
Created on 15/04/2011

@author: yang
'''

class BdeFile(object):
    '''
    classdocs
    '''

    def __init__(self, filename):
        '''
        Constructor
        '''
        self.filename = filename
        self.lines = []
             
    def read(self):
        lines = csv.reader(open(self.filename, 'r'), delimiter="\t")
        for ii, line in enumerate(lines):
            self.lines.append(BdeLine(ii, line))

    def getCountableLines(self):
        return [line for line in self.lines if line.getRecordCode() == 'REC020']


class BdeLine(object):
    '''
    classdocs
    '''

    def __init__(self, index, line):
        '''
        Constructor
        '''
        self.index = index
        self.fields = line
        
    def getLineNumber(self):
        return self.index + 1

    def getRecordCode(self):
        field = self.fields[0]
        return field

    def getJobID(self):
        field = self.fields[4]
        return field
    
    def getEquipmentCode(self):
        field = self.fields[5]
        return field
    
    def getActivityCode(self):
        field = self.fields[6]
        return field

    def getActivityDescription(self):
        field = self.fields[8]
        return field

    def getOperator(self):
        field = self.fields[2]
        return field

    def getDateTime(self):
        field = self.fields[1][:-2]
        return datetime.datetime.strptime(field, "%Y%m%d%H%M%S")
    
    def getImpressionTotal(self):
        field = self.fields[10]
        return int(field)
    
    
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
        
    def show(self):
        for sumup in self.list:
            print '%10s %8.2f  %5d  %5d  %s   %s  %12d' % (sumup.name,
                                                           sumup.calculateDuration(),
                                                           sumup.getFirstLine().getLineNumber(),
                                                           sumup.getLastLine().getLineNumber(),
                                                           sumup.getStartTime(),
                                                           sumup.getEndTime(),
                                                           sumup.calculateImpressionTotal())
    
        

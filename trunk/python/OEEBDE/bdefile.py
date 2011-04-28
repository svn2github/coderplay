#!/usr/bin/env python

import sys
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

    def __init__(self):
        '''
        Constructor
        '''
        self.filename = None
        self.lines = []
             
    def read(self, filename=None):
        if filename == None:
            filename = self.filename
        self.lines = []
        lines = csv.reader(open(filename, 'r'), delimiter="\t")
        for ii, line in enumerate(lines):
            self.lines.append(BdeLine(ii, line))

    def getCountableLines(self):
        return [line for line in self.lines if line.getRecordCode() == 'REC020']
        
    def getLine(self, lineNumber):
        return self.lines[lineNumber-1]


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
        self.sumups = []
    
    def __str__(self):
        return str(self.getLineNumber()) + ': ' + ', '.join(self.fields)
        
    def addSumup(self, sumup):
        self.sumups.append(sumup)
        
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
        
    def getStartedSumups(self):
        sums = []
        for sumup in self.sumups:
            if sumup.getFirstLine() == self:
                sums.append(sumup)
        return sums
    
    def getTerminatedSumups(self):
        sums = []
        for sumup in self.sumups:
            if sumup.getLastLine() == self:
                sums.append(sumup)
        return sums
    
    
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
        self.reporting = None
        
    def addLine(self, line):
        self.lines.append(line);
        line.addSumup(self)
    
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
        stime = sumup.getFirstLine().getDateTime()
        if self.list == []:
            self.list.append(sumup)
        else:
            for idx, element in enumerate(self.list):
                if element.getFirstLine().getDateTime() > stime:
                    self.list.insert(idx, sumup)
                    return
            self.list.append(sumup)
                    
    def __iter__(self):
        return iter(self.list)
        
    def __len__(self):
        return len(self.list)
        
    def __getitem__(self, index):
        return self.list[index]
        
    def show(self):
        for sumup in self.list:
            print '%10s %8.2f  %5d  %5d  %s   %s  %12d' % (sumup.name,
                                                           sumup.calculateDuration(),
                                                           sumup.getFirstLine().getLineNumber(),
                                                           sumup.getLastLine().getLineNumber(),
                                                           sumup.getStartTime(),
                                                           sumup.getEndTime(),
                                                           sumup.calculateImpressionTotal())
    
        
class BdeReporting(object):
    
    def __init__(self):
        self.sumups = []

    def addSumup(self, sumup):
        # Add the sumup in order of start time
        stime = sumup.getFirstLine().getDateTime()
        if self.sumups == []:
            self.sumups.append(sumup)
        else:
            for idx, element in enumerate(self.sumups):
                if element.name != sumup.name:
                    raise BdeException, 'Only one category Sumup can be added into one Reporting.'
                if element.lines[0].getDateTime() > stime:
                    self.sumups.insert(idx, sumup)
                    return
            self.sumups.append(sumup)
        # Mark the sumup's reporting 
        sumup.reporting = self
    
    def getFirstSumup(self):
        return self.sumups[0]
        
    def getLastSumup(self):
        return self.sumups[len(self.sumups)-1]
        
    def calculateDuration(self):
        stime = self.getFirstSumup().getFirstLine().getDateTime()
        etime = self.getLastSumup().getLastLine().getDateTime()
        return (etime-stime).seconds/3600.
        
    def calculateImpressionTotal(self):
        sit = self.getFirstSumup().getFirstLine().getImpressionTotal()
        eit = self.getLastSumup().getLastLine().getImpressionTotal()
        return eit-sit
        
    def getName(self):
        return self.getFirstSumup().name
        
    def merge(self, reporting):
        for sumup in reporting.sumups:
            self.addSumup(sumup)
        

class BdeReportingList(object):
    
    def __init__(self):
        self.list = []
        
    def add(self, reporting):
        self.list.append(reporting)

    def __iter__(self):
        return iter(self.list)
        
    def __len__(self):
        return len(self.list)
        
    def __getitem__(self, index):
        return self.list[index]
        
        
    def show(self):
        for reporting in self.list:
            print '%10s %8.2f  %5d  %5d  %s   %s  %12d' % (reporting.getName(),
                                                           reporting.calculateDuration(),
                                                           reporting.getFirstSumup().getFirstLine().getLineNumber(),
                                                           reporting.getLastSumup().getLastLine().getLineNumber(),
                                                           reporting.getFirstSumup().getStartTime(),
                                                           reporting.getLastSumup().getEndTime(),
                                                           reporting.calculateImpressionTotal())
        
    def report(self, output=sys.stdout):
        for reporting in self.list:
            output.write('0, %d, %s, %s, %s, %0.2f, %d\n' %
                         (reporting.getFirstSumup().getFirstLine().getLineNumber(),
                          reporting.getFirstSumup().getStartTime(),
                          reporting.getFirstSumup().getFirstLine().getJobID(),
                          reporting.getName(),
                          reporting.calculateDuration(),
                          reporting.calculateImpressionTotal()))


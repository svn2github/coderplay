#!/usr/bin/env python

import datetime

'''
Created on 15/04/2011

@author: yang
'''

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
    
    
    

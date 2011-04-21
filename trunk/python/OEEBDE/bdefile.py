#!/usr/bin/env python

import csv
import bdeline
import activitycode
import equipmentcode
import errorcode
import recordcode
from bdeerrorlog import *

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
            self.lines.append(bdeline.BdeLine(ii, line))

    def validation(self):
        errorlog = BdeErrorLog()
        
        found_first_non_at_17_code = False
        
        for line in self.lines:
            
            if line.getRecordID() not in recordcode.lookupTable.keys():
                errorlog.add(1, line)
            
            # Skip if record type is not REC020
            if not recordcode.lookupTable[line.getRecordID()]:
                continue
            
            if line.getEquipmentCode() not in equipmentcode.lookupTable.keys():
                errorlog.add(2, line)
            
            if line.getActivityCode() not in activitycode.lookupTable.keys():
                errorlog.add(3, line)
            
            if found_first_non_at_17_code and line.getActivityCode() != '@17':
                found_first_non_at_17_code = True;
                if line.getJobID() == '0':
                    errorlog.add(5, line)
                    
                if line.getActivityCode() not in ['@95', 'MR']:
                    errorlog.add(6, line)

        
        return errorlog
        
        
    def categorization(self):
        pass
    
    def sumup(self):
        pass
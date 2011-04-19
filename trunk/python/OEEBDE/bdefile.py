#!/usr/bin/env python

import csv
import bdeline
from bdecode import *

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
             
    def readFile(self):
        lines = csv.reader(open(self.filename, 'r'), delimiter="\t")
        for ii, line in enumerate(lines):
            self.lines.append(bdeline.BdeLine(ii, line))

    def validation(self):
        errorlog = BdeErrorLog()
        for line in self.lines:
            
            if line.getRecordID() not in Record.lookupTable.keys():
                errorlog.add(1, line)
            
            # Skip if record type is not REC020
            if not Record.lookupTable[line.getRecordID()]:
                continue
            
            if line.getEquipmentCode() not in Equipment.lookupTable.keys():
                errorlog.add(2, line)
            
            if line.getActivityCode() not in Activity.lookupTable.keys():
                errorlog.add(3, line)
            
            

        
        return errorlog
        
        
    def categorization(self):
        pass
    
    def sumup(self):
        pass
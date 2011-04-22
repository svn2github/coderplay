#!/usr/bin/env python

import csv
import bdeline

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

    def getCountableLines(self):
        return [line for line in self.lines if line.getRecordCode() == 'REC020']


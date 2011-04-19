#!/usr/bin/env python

import csv
import os

'''
Created on 15/04/2011

@author: yang
'''

class Record(object):
    lookupTable = {}
    lookupTable['REC020'] = True
    lookupTable['REC011'] = False
    lookupTable['REC001'] = False

class Equipment(object):
    
    file = 'C:/Users/yang/programs/oeebde/equipcode'
    lines = csv.reader(open(os.path.abspath(file), 'r'))
    lookupTable = {}
    for line in lines:
        code = line[0]
        value = line[1]
        lookupTable[code] = value
    
    @staticmethod
    def getName(code):
        return Equipment.lookupTable[str(code)]



class Activity(object):
    
    file = 'C:/Users/yang/programs/oeebde/activitycode'
    lines = csv.reader(open(file, 'r'), delimiter="\t")
    lookupTable = {}
    for line in lines:
        code = line[0]
        value = line[1:]
        lookupTable[code] = value
        
    @staticmethod
    def getName(code):
        return Activity.lookupTable[str(code)][0]
    
    @staticmethod
    def getStatus(code):
        return Activity.lookupTable[str(code)][1]
        
    @staticmethod
    def getDescription(code):
        return Activity.lookupTable[str(code)][2]


class Error(object):
    '''
    classdocs
    '''
    file = 'C:/Users/yang/programs/oeebde/errorcode'
    f = open(file, "r")
    lines = f.readlines()
    lookupTable = {}
    for line in lines:
        code, value = (int(line[:4]), line[4:])
        lookupTable[code] = value

    def __init__(self, code, line):
        '''
        Constructor
        '''
        self.code = code;
        self.line = line
                   
    @staticmethod
    def getDescription(code):
        return Error.lookupTable[code]
        


class BdeErrorLog(object):

        
    def __init__(self):
        self.errorList = []
        
    def add(self, code, line):
        self.errorList.append(Error(code, line))
        
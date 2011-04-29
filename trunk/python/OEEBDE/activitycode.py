#!/usr/bin/env python

import csv
import bdeutil

def getName(code):
    return lookupTable[str(code)][0]

def getStatus(code):
    return lookupTable[str(code)][1]
    
def getDescription(code):
    return lookupTable[str(code)][2]

def fillLookupTable(file='activitycode'):
    '''
    Build the activity lookup table
    '''
    lookupTable = {}
    lines = csv.reader(open(file, 'r'), delimiter="\t")
    for line in lines:
        code = line[0]
        value = line[1:]
        lookupTable[code] = value
    return lookupTable
    

# The lookup table 
lookupTable = fillLookupTable()


if __name__ == '__main__':
    print lookupTable

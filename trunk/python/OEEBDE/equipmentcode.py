#!/usr/bin/env python

import csv
import os

def fillLookupTable(file='equipmentcode'):
    lines = csv.reader(open(file, 'r'))
    lookupTable = {}
    for line in lines:
        code = line[0]
        value = line[1]
        lookupTable[code] = value
    return lookupTable
        
def getName(code):
    return Equipment.lookupTable[str(code)]

lookupTable = fillLookupTable()

if __name__ == '__main__':
    print lookupTable
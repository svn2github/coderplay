#!/usr/bin/env python

def fillLookupTable(file='errorcode'):
    lines = open(file, "r").readlines()
    lookupTable = {}
    for line in lines:
        code, value = (int(line[:4]), line[4:])
        lookupTable[code] = value
    return lookupTable

def getDescription(code):
    return lookupTable[code]
    
lookupTable = fillLookupTable()

if __name__ == '__main__':
    print lookupTable
    

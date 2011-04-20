#!/usr/bin/env python

import csv

_file = 'activitycode'
_lines = csv.reader(open(_file, 'r'), delimiter="\t")

# The lookup table and code categories
lookupTable = {}
Prod = []
MR = []
Wup = []
Downtime = []

def getName(code):
    return lookupTable[str(code)][0]

def getStatus(code):
    return lookupTable[str(code)][1]
    
def getDescription(code):
    return lookupTable[str(code)][2]

# Build the variables
for _line in _lines:
    _code = _line[0]
    _value = _line[1:]
    # Build the activity lookup table
    lookupTable[_code] = _value
    # Set the categories of the code
    name = getName(_code)
    if name == 'Prod':
        Prod.append(_code)
    elif name == 'MR':
        MR.append(_code)
    elif name == 'Wup' and getStatus(_code) != '':
        Wup.append(_code)
    elif name == 'Downtime':
        Downtime.append(_code)
        
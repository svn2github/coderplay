#!/usr/bin/env python

_file = 'errorcode'
_lines = open(_file, "r").readlines()
lookupTable = {}

def getDescription(code):
    return Error.lookupTable[code]
    
for _line in _lines:
    _code, _value = (int(_line[:4]), _line[4:])
    lookupTable[_code] = _value

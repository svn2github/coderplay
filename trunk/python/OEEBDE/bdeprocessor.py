#!/usr/bin/env python

from bdefile import BdeFile
'''
Created on 15/04/2011

@author: yang
'''

bde = BdeFile('C:/Users/yang/programs/oeebde/good.bde')
bde.readFile()
    
print bde.lines[0].fields
print len(bde.lines[0].fields)
line = bde.lines[0]
print line.getDateTime()
print line.getImpressionCount()


a = bde.validation()

print a



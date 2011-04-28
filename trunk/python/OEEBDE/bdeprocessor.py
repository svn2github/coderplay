#!/usr/bin/env python

from bdeerror import BdeErrorLog
from bdefile import BdeFile, BdeSumup, BdeSumupList, BdeReporting, BdeReportingList
from bdedb import BdeDB
import activitycode
import bdeutil
import validationrules
import sumuprules
import reportingrules

'''
Created on 15/04/2011

@author: yang
'''

# Read the BDE file into file object
file = BdeFile()
file.read('good.bde')
    
# Create the sqlite DB for data validations
# Load the file into the Database
# This creates a memory concern that we now have two copies of the file.
# One in the file object and this one in sqlite database.
db = BdeDB()
db.loaddata('good.bde')

# The error logger
errorlog = BdeErrorLog()

# Build the validation rules from the xml files
validationRules = validationrules.buildValidationRules()
    
# Perform data validations
for rule in validationRules.itervalues():
    rule.action(db.cursor, errorlog)

# Be nice and delete the database for saving memories
del(db)

# Print any errors found
errorlog.show()



# Build the Sumup Rules object
sumupRules = sumuprules.bulidSumupRules()

# The overall sumup list
sumupList = BdeSumupList()

# Set every sumup to be None at the beginning, meaning
# no sumup is current happening.
categoryNames = activitycode.codeOf.keys()
sumupCurrent = {}
for categoryName in categoryNames:
    sumupCurrent[categoryName] = None
    
# Lines that are not used for any sumups
unCategoryLines = []

# Data sum-ups
for line in file.getCountableLines():
    # Which category the code belongs to
    categoryName = activitycode.findCategory(line.getActivityCode())
    
    # Process the code from this line belongs to a required category
    if categoryName is not None:
        sumupRules[categoryName].action(line, sumupCurrent, sumupList)
    else:
        unCategoryLines.append(line)
        
# End any unfinished sumup at the end of the file
for categoryName in sumupCurrent.keys():
    if sumupCurrent[categoryName] is not None:
        sumupList.add(sumupCurrent[categoryName])
        sumupCurrent[categoryName] = None
        
#sumupList.show()



# Reporting based on the sumups

# Build the reporting Rules object
reportRules = reportingrules.buildReportingRules()
    
# Create the reportings
reportingList = BdeReportingList()
for idx, sumup in enumerate(sumupList):
    if sumup.name not in reportRules.keys():
        continue
    reportRules[sumup.name].action(idx, sumupList, reportingList)
    

reportingList.show()
#reportingList.report()




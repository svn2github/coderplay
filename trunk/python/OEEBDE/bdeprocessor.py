#!/usr/bin/env python

from bdeerrorlog import BdeErrorLog
from bdefile import BdeFile
from bdeconfig import BdeConfig
from bdedb import BdeDB
from bdesumup import BdeSumup, BdeSumupList
import activitycode
import bdeutil
import bdesumuprules

'''
Created on 15/04/2011

@author: yang
'''

# Read the file into file object
file = BdeFile('good.bde')
file.read()
    
# Process the config file
config = BdeConfig()
config.read()

# Create the sqlite DB for data validations
# Load the file into the Database
# This creates a memory concern that we now have two copies of the file.
# One in the file object and this one in sqlite database.
db = BdeDB()
db.loaddata('good.bde')

# The error logger
errorlog = BdeErrorLog()

# Perform required data validations based on the config file
# Add any error into the error logger
for option in config.validationOptions:
    code, lineIndex = option.routine(db.cursor)
    for index in lineIndex:
            if index is not None:
                errorlog.add(code, file.lines[index])
            else:
                errorlog.add(code, None)

# Be nice and delete the database
del(db)

# Print any errors found
for error in errorlog.errorList:
    print error[0], ': ', error[1].getLineNumber()

# The overall sumup list
sumupList = BdeSumupList()

# Set every sumup to be None at the beginning, meaning
# no sumup is current happening.
categoryNames = activitycode.codeOf.keys()
sumupCurrent = {}
for categoryName in categoryNames:
    sumupCurrent[categoryName] = None
    
# Build the Sumup Rules object
sumupRules = {}
for categoryName in categoryNames:
    tree = bdeutil.readXMLTree()
    node = tree.find('Sumups/Categories')
    for element in node.getiterator('Category'):
        if element.attrib['Name'] == categoryName:
            ruleElement = element.find('Rule')
            sumupRules[categoryName] = bdesumuprules.SumupRule(categoryName, ruleElement.text)
            for extraElement in ruleElement.getiterator():
                sumupRules[categoryName].setattr(extraElement.tag, extraElement.text)
            
            # Set the routine that process the sumup
            rulesNode = tree.find('Sumups/Rules')
            moduleName = rulesNode.attrib['Module']
            functionName = rulesNode.find(sumupRules[categoryName].ruleName).attrib['function']
            moduleName = __import__(moduleName)
            sumupRules[categoryName].setRoutine(getattr(moduleName, functionName))
                
            # Get out of node loop once match is found
            break;

# Data sum-ups
for line in file.getCountableLines():
    # Which category the code belongs to
    categoryName = activitycode.findCategory(line.getActivityCode())
    
    # Process the category's sumup is it is not None
    if categoryName is not None:
        sumupRules[categoryName].action(line, sumupCurrent, sumupList)
        
# End any unfinished sumup at the end of the file
for categoryName in sumupCurrent.keys():
    if sumupCurrent[categoryName] is not None:
        sumupList.add(sumupCurrent[categoryName])
        sumupCurrent[categoryName] = None
        
    
for sumup in sumupList.list:
    print '%10s %8.2f  %s   %s  %12d' % (sumup.name, sumup.calculateDuration(), sumup.getStartTime(), sumup.getEndTime(), sumup.calculateImpressionTotal())



#!/usr/bin/env python

from bdeerror import BdeErrorLog
from bdefile import BdeFile, BdeSumup, BdeSumupList, BdeReporting, BdeReportingList
from bdeconfig import BdeConfig
from bdedb import BdeDB
import activitycode
import bdeutil
import bdevalidationrules
import bdesumuprules
import reportingrules

'''
Created on 15/04/2011

@author: yang
'''

# Read the BDE file into file object
file = BdeFile('good.bde')
file.read()
    
# Create the sqlite DB for data validations
# Load the file into the Database
# This creates a memory concern that we now have two copies of the file.
# One in the file object and this one in sqlite database.
db = BdeDB()
db.loaddata('good.bde')

# The error logger
errorlog = BdeErrorLog()

# Read the XML file for data validation settings
validationRules = {}
tree = bdeutil.readXMLTree()
node = tree.find('Validations/Action')
for ruleElement in node.getiterator('Rule'):
    ruleName = ruleElement.attrib['Name']
    # create the rule object
    thisRule = bdevalidationrules.ValidationRule(ruleName)
    # get any additional variables
    bdeutil.readRuleVars(ruleElement, thisRule)
    # Set the routine
    for r in tree.find('Validations/Rules').getiterator('Rule'):
        if r.attrib['Name'] == ruleElement.attrib['Name']:
            moduleName = r.attrib['Module']
            functionName = r.attrib['Function']
            moduleName = __import__(moduleName)
            thisRule.routine = getattr(moduleName, functionName)
            break
    validationRules[ruleName] = thisRule
            
    
# Perform data validations
for rule in validationRules.itervalues():
    rule.action(db.cursor, errorlog)


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
tree = bdeutil.readXMLTree()
node = tree.find('Sumups/Categories')
for element in node.getiterator('Category'):
    categoryName = element.attrib['Name']
    # Create the rule object
    thisRule = bdesumuprules.SumupRule(categoryName)
    
    # Process the start rule
    ruleElement = element.find('StartRule')
    # The rule name
    thisRule.startSumupRule = ruleElement.attrib['Name']
    # Get any additional variables
    bdeutil.readRuleVars(ruleElement, thisRule)
    # Set the routine 
    rulesNode = tree.find('Sumups/Rules/StartRules/'+thisRule.startSumupRule)
    moduleName = rulesNode.attrib['Module']
    functionName = rulesNode.attrib['Function']
    moduleName = __import__(moduleName)
    thisRule.startSumupRoutine = getattr(moduleName, functionName)
    
    # Process the terminate rule
    ruleElement = element.find('TerminateRule')
    # The rule name
    thisRule.terminateSumupRule = ruleElement.attrib['Name']
    # Get any additional variables
    bdeutil.readRuleVars(ruleElement, thisRule)
    # Set the routine 
    rulesNode = tree.find('Sumups/Rules/TerminateRules/'+thisRule.terminateSumupRule)
    moduleName = rulesNode.attrib['Module']
    functionName = rulesNode.attrib['Function']
    moduleName = __import__(moduleName)
    thisRule.terminateSumupRoutine = getattr(moduleName, functionName)
    
    # Process the end rule
    ruleElement = element.find('EndRule')
    # The rule name
    thisRule.endSumupRule = ruleElement.attrib['Name']
    # Get any additional variables
    bdeutil.readRuleVars(ruleElement, thisRule)
    # Set the routine 
    rulesNode = tree.find('Sumups/Rules/EndRules/'+thisRule.endSumupRule)
    moduleName = rulesNode.attrib['Module']
    functionName = rulesNode.attrib['Function']
    moduleName = __import__(moduleName)
    thisRule.endSumupRoutine = getattr(moduleName, functionName)
    
    # This one rule is now complete
    sumupRules[categoryName] = thisRule
        

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
reportRules = {}
tree = bdeutil.readXMLTree()
node = tree.find('Reporting/Categories')
for element in node.getiterator('Category'):
    categoryName = element.attrib['Name']
    thisRule = reportingrules.ReportingRule(categoryName)
    for ruleElement in element.find('Rules').getiterator('Rule'):
        thisRule.addReportRule(ruleElement.attrib['Name'])
        # Looking for the rule description
        for r in tree.find('Reporting/Rules').getiterator('Rule'):
            if r.attrib['Name'] == ruleElement.attrib['Name']:
                moduleName = r.attrib['Module']
                functionName = r.attrib['Function']
                moduleName = __import__(moduleName)
                thisRule.addReportRoutine(getattr(moduleName, functionName))
                break
        # Read any variables
        bdeutil.readRuleVars(ruleElement, thisRule)
        
    # This rule is now complete
    reportRules[categoryName] = thisRule
    
    
reportingList = BdeReportingList()
for idx, sumup in enumerate(sumupList):
    if sumup.name not in reportRules.keys():
        continue
    reportRules[sumup.name].action(idx, sumupList, reportingList)
    

reportingList.show()
reportingList.report()




#!/usr/bin/env python

import sys
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

class ProcessorConfig(object):
    
    def __init__(self):
        self.inputfile = None
        self.outputfile = sys.stdout
        self.verbose = False
        self.debug = False
        self.rulesxml = 'bderules.xml'
        self.settingsxml = 'bdesettings.xml'


class ProcessorResult(object):

    def __init__(self):
        self.errorlog = None
        self.sumupList = None
        self.reportingList = None
        self.unCategoryLines = []
    

def bdeprocessor(config):

    # Create the result object
    result = ProcessorResult()

    # Create the sqlite DB for data validations
    # Load the file into the Database
    db = BdeDB()
    db.loaddata(config.inputfile)
    
    # The error logger
    errorlog = BdeErrorLog()
    
    # Build the validation rules from the xml files
    validationRules = validationrules.buildValidationRules(config.rulesxml, config.settingsxml)
        
    # Perform data validations
    for rule in validationRules.itervalues():
        rule.action(db.cursor, errorlog)
    
    # Be nice and delete the database for saving memories
    del(db)
    
    # Read the BDE file into file object
    # The file object is created after deleting the database object
    # to avoid having two copies of the file.
    bdefile = BdeFile()
    bdefile.read(config.inputfile)
        
    # Print any errors found
    errorlog.show(bdefile, verbose=config.verbose)
    result.errorlog = errorlog
    
    # Abort the run if any data validation fails
    if errorlog.hasError():
        print ''
        print 'Data validation failed. Program execution aborted.'
        return result
    else:
        print 'Data validation PASSED.'
    
    
    # Build the Sumup Rules object
    sumupRules = sumuprules.bulidSumupRules(config.rulesxml, config.settingsxml)
    
    # The overall sumup list
    sumupList = BdeSumupList()
    
    # Set every sumup to be None at the beginning, meaning
    # no sumup is current happening.
    categoryNames = activitycode.codeOf.keys()
    sumupCurrent = {}
    for categoryName in categoryNames:
        sumupCurrent[categoryName] = None
        
    
    # Data sum-ups
    for line in bdefile.getCountableLines():
        # Which category the code belongs to
        categoryName = activitycode.findCategory(line.getActivityCode())
        
        # Process the code from this line belongs to a required category
        if categoryName is not None:
            sumupRules[categoryName].action(line, sumupCurrent, sumupList)
        else: # Lines that are not used for any sumups
            result.unCategoryLines.append(line)
            
    # End any unfinished sumup at the end of the file
    for categoryName in sumupCurrent.keys():
        if sumupCurrent[categoryName] is not None:
            sumupList.add(sumupCurrent[categoryName])
            sumupCurrent[categoryName] = None
            
    print 'Data sumup finished.'
    if config.debug:
        sumupList.show()
    result.sumupList = sumupList
    
    
    # Reporting based on the sumups
    
    # Build the reporting Rules object
    reportRules = reportingrules.buildReportingRules(config.rulesxml, config.settingsxml)
        
    # Create the reportings
    reportingList = BdeReportingList()
    for idx, sumup in enumerate(sumupList):
        if sumup.name not in reportRules.keys():
            continue
        reportRules[sumup.name].action(idx, sumupList, reportingList)
        
    print 'Data reporting finished.'
    if config.debug:
        reportingList.show()
    reportingList.report(config.outputfile)
    result.reportingList = reportingList

    return result


if __name__ == '__main__':
    config = ProcessorConfig()
    config.inputfile = 'good.bde'
    config.verbose = True
    config.debug = True
    
    result = bdeprocessor(config)
    


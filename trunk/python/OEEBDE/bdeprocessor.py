#!/usr/bin/env python

"""
Apr. 15, 2011

@autor Yang Wang

Followings are for doctest.

>>> main()
Data validation PASSED.
Data sumup finished.
Data reporting finished.
0, 1, 2010-08-02 16:00:29, 66604, MR, 0.70, 1222
0, 63, 2010-08-02 16:31:34, 66604, W-up, 0.18, 934
0, 92, 2010-08-02 16:42:25, 66604, Prod, 1.10, 1816
0, 99, 2010-08-02 16:42:33, 66604, W-up, 1.10, 1816
0, 123, 2010-08-02 16:48:57, 66604, Downtime, 0.99, 1308
0, 285, 2010-08-02 17:48:36, 66604, MR, 0.46, 939
0, 340, 2010-08-02 18:16:18, 66604, Prod, 0.24, 1824
0, 382, 2010-08-02 18:28:37, 66604, W-up, 0.04, 0
0, 388, 2010-08-02 18:29:01, 66604, Downtime, 0.03, 0
0, 398, 2010-08-02 18:31:14, 66604, MR, 0.33, 374
0, 446, 2010-08-02 18:51:12, 66604, Prod, 0.36, 2330
0, 521, 2010-08-02 19:08:43, 66604, W-up, 0.07, 0
0, 527, 2010-08-02 19:09:00, 66604, Downtime, 0.06, 0
0, 539, 2010-08-02 19:12:43, 66604, MR, 0.97, 2775
0, 607, 2010-08-02 19:47:15, 66604, Downtime, 0.06, 0
0, 608, 2010-08-02 19:47:23, 66604, W-up, 0.06, 0
0, 665, 2010-08-02 20:11:07, 66604, Prod, 0.42, 2739
0, 711, 2010-08-02 20:33:20, 66604, W-up, 0.05, 0
0, 717, 2010-08-02 20:34:00, 66604, Downtime, 0.04, 0
0, 728, 2010-08-02 20:36:07, 66604, MR, 0.26, 258
0, 767, 2010-08-02 20:51:33, 66604, Prod, 0.30, 2434
0, 799, 2010-08-02 21:05:33, 66604, Downtime, 0.07, 0
0, 801, 2010-08-02 21:06:56, 66604, W-up, 0.05, 0
0, 816, 2010-08-02 21:09:48, 66604, MR, 0.77, 2754
0, 888, 2010-08-02 21:43:10, 66604, W-up, 0.13, 0
0, 900, 2010-08-02 21:44:00, 66604, Downtime, 0.12, 0
"""

import os
import sys
from bdeerror import BdeErrorLog
from bdefile import BdeFile, BdeSumupList, BdeReportingList
from bdedb import BdeDB
import bdeutil
import validationrules
import sumuprules
import reportingrules


class ProcessorConfig(object):
    
    def __init__(self):
        self.inputfile = None
        self.outputfile = None
        self.outputstream = sys.stdout
        self.verbose = False
        self.debug = False
        # The XML file is assumed to be in the same directory as the source
        # file. So we build the complete path to the file based on it.
        srcdir = os.path.dirname(os.path.abspath(__file__))
        self.rulesxml = os.path.join(srcdir, 'bderules.xml')
        self.settingsxml = os.path.join(srcdir, 'bdesettings.xml')
        
    def readXMLConfig(self, settingsxml=None):
        if settingsxml is None:
            settingsxml = self.settingsxml
        else:
            self.settingsxml = settingsxml
            
        tree = bdeutil.readXMLTree(settingsxml)
        node = tree.find('General')
        
        inputfile = node.find('InputFile').text
        if inputfile is not None:
            self.inputfile = inputfile
            
        outputfile = node.find('OutputFile').text
        if outputfile is not None:
            self.outputfile = outputfile
            self.outputstream = open(outputfile, 'w')
            
        if node.find('Verbose').text == 'true':
            self.verbose = True
        else:
            self.verbose = False
        if node.find('Debug').text == 'true':
            self.debug = True
        else:
            self.debug = False


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
    sumupRules = sumuprules.buildSumupRules(config.rulesxml, config.settingsxml)
    
    # The overall sumup list
    sumupList = BdeSumupList()
    
    # Set every sumup to be None at the beginning, meaning
    # no sumup is current happening.
    categoryNames = sumupRules.keys()
    sumupCurrent = {}
    for categoryName in categoryNames:
        sumupCurrent[categoryName] = None
        
    
    # Data sum-ups
    for line in bdefile.getCountableLines():
        # Which category the code belongs to
        categoryName = sumuprules.findCategory(line.getActivityCode())
        
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
    reportingList.report(config.outputstream)
    result.reportingList = reportingList

    return result

def main():
    config = ProcessorConfig()
    config.readXMLConfig()
    config.verbose = False
    config.debug = False
    result = bdeprocessor(config)
    
if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    


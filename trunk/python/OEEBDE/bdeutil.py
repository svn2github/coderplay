#!/usr/bin/env python

import os
import inspect
import datetime
import xml.etree.ElementTree as ET

def whoami():
    return inspect.stack()[1][3]

def whosdaddy():
    return inspect.stack()[2][3]

def convertDateTimeToField2(thistime):
    return int(str(thistime)[:-4].replace('-','').replace(' ','').replace(':','').replace('.',''))
    
def readXMLTree(file='bdesettings.xml'):
    # The XML file is assumed to be in the same directory as the source
    # file. So we build the complete path to the file based on it.
    srcdir = os.path.dirname(os.path.abspath(__file__))
    # Parse the XML file
    xmlfile = os.path.join(srcdir, file)
    tree = ET.parse(xmlfile)
    return tree

def getConcatenatableSumup(sumup1, sumup2):
    name1 = [element.name for element in sumup1]
    name2 = [element.name for element in sumup2]
    
    commonNames = [element for element in name1 if element in name2]
    
    return [element for element in sumup1 if element.name in commonNames], \
           [element for element in sumup2 if element.name in commonNames]
    
def readRuleVars(ruleElement, ruleobj):
    convertDict = {'int': int, 'float': float, 'str': str}
    for varElement in ruleElement.getiterator('Variable'):
        name = varElement.attrib['Name']
        type = varElement.attrib['Type']
        value = convertDict[type](varElement.attrib['Value'])
        
        if varElement.attrib['List'] != '0': # list
            ruleobj.addListAttr(name, value)
        else: # scalar
            ruleobj.setattr(name, value)
        
def readRuleRoutine(ruleName, rulesNode):
    for r in rulesNode.getiterator('Rule'):
        if r.attrib['Name'] == ruleName:
            moduleName = r.attrib['Module']
            functionName = r.attrib['Function']
            moduleName = __import__(moduleName)
            return getattr(moduleName, functionName)


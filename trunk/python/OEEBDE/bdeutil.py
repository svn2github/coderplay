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
    
def readXMLTree(xmlfile):
    # Parse the XML file and return the tree data object
    tree = ET.parse(xmlfile)
    return tree

def getConcatenatableSumup(sumup1, sumup2):
    name1 = [element.name for element in sumup1]
    name2 = [element.name for element in sumup2]
    
    commonNames = [element for element in name1 if element in name2]
    
    return [element for element in sumup1 if element.name in commonNames], \
           [element for element in sumup2 if element.name in commonNames]
    
def readRuleVars2(ruleElement, ruleobj, ruledef):
    
    allvars = ruledef.variables.keys()
    for varElement in ruleElement.getiterator('Variable'):
        varname = varElement.attrib['Name']
        varvalue = ruledef.variables[varname].type(varElement.attrib['Value'])
        if ruledef.variables[varname].isList:
            ruleobj.addListAttr(varname, varvalue)
        else: # scalar
            ruleobj.setattr(varname, varvalue)
        try:
            allvars.remove(varname)
        except ValueError:
            continue
    # Set default value for any unprovided variables
    for varname in allvars:
        if ruledef.variables[varname].value is not None:
            if ruledef.variables[varname].isList:
                ruleobj.addListAttr(varname, ruledef.variables[varname].value)
            else: # scalar
                ruleobj.setattr(varname, ruledef.variables[varname].value)


class RuleVariable(object):
    
    def __init__(self, varname, vartype, isList, varvalue):
        self.name = varname
        self.type = vartype
        self.isList = isList
        self.value = varvalue
        
class RuleDefinition(object):
    
    def __init__(self, ruleName, ruleRoutine, variables={}):
        self.name = ruleName
        self.routine = ruleRoutine
        self.variables = variables
        

def readRuleDefintiion(ruleName, rulesNode):
    for r in rulesNode.getiterator('Rule'):
        if r.attrib['Name'] == ruleName:
            moduleName = r.attrib['Module']
            functionName = r.attrib['Function']
            moduleName = __import__(moduleName)
            # Read any additional variables for the rule
            variables = {}
            convertDict = {'int': int, 'float': float, 'str': str}
            varsNode = r.find('Variables')
            if varsNode is not None:
                for varElement in varsNode.getiterator('Variable'):
                    varname = varElement.attrib['Name']
                    vartype = varElement.attrib['Type']
                    if varElement.attrib['List'] == 'true':
                        isList = True
                    else:
                        isList = False
                    varvalue = varElement.attrib['DefaultValue']
                    if varvalue == '':
                        varvalue = None
                    else:
                        varvalue = convertDict[vartype](varvalue)
                    variables[varname] = RuleVariable(varname, convertDict[vartype], isList, varvalue)
            
            # Now we have the full definition of the rule
            return RuleDefinition(ruleName, getattr(moduleName, functionName), variables)




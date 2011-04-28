#!/usr/bin/env python

import activitycode
from bdefile import BdeSumup
import bdeutil

class SumupRule(object):
    def __init__(self, categoryName):
        self.categoryName = categoryName
        self.startSumupRule = None
        self.terminateSumupRule = None
        self.endSumupRule = None
        self.startSumupRoutine = None
        self.terminateSumupRoutine = None
        self.endSumupRoutine = None
        
    def setattr(self, name, value):
        setattr(self, name, value)
            
    def addListAttr(self, name, value):
        # Make the attribute's value a list if multiple value is going to be inserted.
        theattr = self.getattr(name)
        if theattr is None:
            tmp = []
            tmp.append(value)
            setattr(self, name, tmp)
        elif type(theattr).__name__ == 'list':
            theattr.append(value)
            setattr(self, name, theattr)
        else:
            theattr = [theattr]
            theattr.append(value)
            setattr(self, name, theattr)
        
    def getattr(self, name):
        try:
            return getattr(self, name)
        except AttributeError:
            return None
        
    def action(self, line, sumupCurrent, sumupList):
        categoryName = self.categoryName
        # If no sumup of this category is running
        if sumupCurrent[categoryName] is None:
            # Start own sumup?
            self.startSumupRoutine(line, self, sumupCurrent, sumupList)
            # Terminate any other sumups by requirement?
            self.terminateSumupRoutine(line, self, sumupCurrent, sumupList)
            
        else: # If a sumup of this category is already running
            # End own sumup?
            self.endSumupRoutine(line, self, sumupCurrent, sumupList)
            

def bulidSumupRules(rulesxml='bderules.xml', settingsxml='bdesettings.xml'):
    sumupRules = {}
    tree = bdeutil.readXMLTree(settingsxml)
    node = tree.find('Sumups/Categories')
    for element in node.getiterator('Category'):
        categoryName = element.attrib['Name']
        # Create the rule object
        thisRule = SumupRule(categoryName)
        
        # Process the start rule
        ruleElement = element.find('StartRule')
        # The rule name
        thisRule.startSumupRule = ruleElement.attrib['Name']
        # Get any additional variables
        bdeutil.readRuleVars(ruleElement, thisRule)
        # Set the routine 
        thisRule.startSumupRoutine = bdeutil.readRuleRoutine(ruleElement.attrib['Name'],
                                                             bdeutil.readXMLTree(rulesxml).find('Sumups/Rules/StartRules'))
        
        # Process the terminate rule
        ruleElement = element.find('TerminateRule')
        # The rule name
        thisRule.terminateSumupRule = ruleElement.attrib['Name']
        # Get any additional variables
        bdeutil.readRuleVars(ruleElement, thisRule)
        # Set the routine 
        thisRule.terminateSumupRoutine = bdeutil.readRuleRoutine(ruleElement.attrib['Name'],
                                                                 bdeutil.readXMLTree(rulesxml).find('Sumups/Rules/TerminateRules'))
        
        # Process the end rule
        ruleElement = element.find('EndRule')
        # The rule name
        thisRule.endSumupRule = ruleElement.attrib['Name']
        # Get any additional variables
        bdeutil.readRuleVars(ruleElement, thisRule)
        # Set the routine 
        thisRule.endSumupRoutine = bdeutil.readRuleRoutine(ruleElement.attrib['Name'],
                                                           bdeutil.readXMLTree(rulesxml).find('Sumups/Rules/EndRules'))
        
        # This one rule is now complete
        sumupRules[categoryName] = thisRule
            
    return sumupRules



def rule_SR_Whenever(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    ifnot = sumupRule.getattr('ifnot')
    if type(ifnot).__name__ == 'list':
        for ifnotcate in ifnot:
            if sumupCurrent[ifnotcate] is not None:
                return
    else:
        if ifnot is not None and sumupCurrent[ifnot] is not None:
            return
    sumupCurrent[categoryName] = BdeSumup(categoryName)
    sumupCurrent[categoryName].addLine(line)

def rule_SR_OnCode(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    ifnot = sumupRule.getattr('ifnot')
    if type(ifnot).__name__ == 'list':
        for ifnotcate in ifnot:
            if sumupCurrent[ifnotcate] is not None:
                return
    else:
        if ifnot is not None and sumupCurrent[ifnot] is not None:
            return
    if line.getActivityCode() == sumupRule.startCode:
        sumupCurrent[categoryName] = BdeSumup(categoryName)
        sumupCurrent[categoryName].addLine(line)
    
def rule_SR_Wup(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    if activitycode.getStatus(line.getActivityCode()) == 'ON':
        sumupCurrent[categoryName] = BdeSumup(categoryName)
        sumupCurrent[categoryName].addLine(line)
        sumupCurrent[categoryName].status += 1

def rule_TR_All(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    for tname in sumupCurrent.keys():
        if tname == categoryName:
            continue
        exceptCategory = sumupRule.getattr('except')
        if exceptCategory is not None:
            if type(exceptCategory).__name__ == 'list' and tname in exceptCategory:
                continue
            elif tname == exceptCategory:
                continue
        if sumupCurrent[tname] is not None:
            sumupCurrent[tname].addLine(line) # add the terminate line
            sumupList.add(sumupCurrent[tname])
            sumupCurrent[tname] = None
    
def rule_TR_None(line, sumupRule, sumupCurrent, sumupList):
    pass

def rule_ER_ByOthers(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    sumupCurrent[categoryName].addLine(line)

def rule_ER_OnCode(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    sumupCurrent[categoryName].addLine(line)
    if line.getActivityCode() == sumupRule.endCode:
        # Self-termination
        sumupList.add(sumupCurrent[categoryName])
        sumupCurrent[categoryName] = None
            
def rule_ER_Wup(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    sumupCurrent[categoryName].addLine(line)
    if activitycode.getStatus(line.getActivityCode()) == 'ON':
        sumupCurrent[categoryName].status + 1
    if activitycode.getStatus(line.getActivityCode()) == 'OFF':
        sumupCurrent[categoryName].status - 1
    # Do we need now terminate the sumup based on the status
    if sumupCurrent[categoryName].status == 0:
        # special self-termination
        sumupList.add(sumupCurrent[categoryName])
        sumupCurrent[categoryName] = None


#!/usr/bin/env python

import activitycode
from bdefile import BdeSumup

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
            setattr(self, name, [].extend(value))
        elif type(theattr).__name__ == 'list':
            setattr(self, name, theattr.extend(value))
        else:
            setattr(self, name, [theattr].extend(value))
        
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


#!/usr/bin/env python
from bdeerror import BdeException
import bdeutil
from bdefile import BdeReporting

class ReportingRule(object):
    
    def __init__(self, categoryName):
        self.categoryName = categoryName
        self.reportRules = []
        self.reportRoutines = []
    
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
        
    def addReportRule(self, reportRuleName):
        self.reportRules.append(reportRuleName)
        
    def addReportRoutine(self, reportRoutine):
        self.reportRoutines.append(reportRoutine)
        
    def action(self, idx, sumupList, reportingList):
        for routine in self.reportRoutines:
            reporting = routine(idx, sumupList, self)
            if reporting is not None:
                reportingList.add(reporting)
    

def rule_None(idx, sumupList, reportRule):
    theSum = sumupList[idx]
    if theSum.reporting is not None:
        return None
    
    reporting = BdeReporting()
    
    reporting.addSumup(theSum)
    return reporting


def rule_Concatenate(idx, sumupList, reportRule):
    theSum = sumupList[idx]
    if theSum.reporting is not None:
        return None
    
    reporting = BdeReporting()
    
    duration = theSum.calculateDuration()
    impressionTotal = theSum.calculateImpressionTotal()
    
    if duration > reportRule.SIG_DURATION and impressionTotal > reportRule.SIG_IMPCOUNT:
        reporting.addSumup(theSum)
        return reporting
    
    if idx == 0 or idx == len(sumupList)-1:
        reporting.addSumup(theSum)
        return reporting
    
    sumTerminatedByFirstLine = theSum.getFirstLine().getTerminatedSumups()
    if sumTerminatedByFirstLine == []:
        reporting.addSumup(theSum)
        return reporting
    
    sumStartedByLastLine = theSum.getLastLine().getStartedSumups()
    if sumStartedByLastLine == []:
        reporting.addSumup(theSum)
        return reporting
    
    preSum, postSum = bdeutil.getConcatenatableSumup(sumTerminatedByFirstLine, sumStartedByLastLine)
    
    if preSum == [] or postSum == []:
        reporting.addSumup(theSum)
        return reporting
    
    if len(preSum) != 1 or len(postSum) != 1:
        raise BdeException, 'More than one concatenation candidates found.'
    
    preSum = preSum[0]
    postSum = postSum[0]
    
    if postSum.reporting is not None:
        raise BdeException, 'Sumup is already assigned to another reporting.'
    
    if preSum.reporting is None:
        raise BdeException, 'Sumup does not belong to any reporting.'
    
    # Concatenate
    preSum.reporting.addSumup(postSum)
    
    return None
    
def rule_MergeAdjacent(idx, sumupList, reportRule):
    theSum = sumupList[idx]
    if theSum.reporting is not None:
        return None
    
    reporting = BdeReporting()
    
    duration = theSum.calculateDuration()
    impressionTotal = theSum.calculateImpressionTotal()
    
    if duration > reportRule.SIG_DURATION and impressionTotal > reportRule.SIG_IMPCOUNT:
        reporting.addSumup(theSum)
        return reporting
    
    if idx == 0:
        reporting.addSumup(theSum)
        return reporting
    
    sumTerminatedByFirstLine = theSum.getFirstLine().getTerminatedSumups()
    if sumTerminatedByFirstLine == []:
        reporting.addSumup(theSum)
        return reporting
    
def rule_ConvertIfCode(idx, sumupList, reportRule):
    theSum = sumupList[idx]
    if theSum.reporting is not None:
        return None
    
    if theSum.name != reportRule.from_sumup:
        return None
    
    for line in theSum.lines:
        if line.getActivityCode() not in reportRule.onlycodes:
            return None
        
    theSum.name = reportRule.to_sumup
    
    return None
    
    
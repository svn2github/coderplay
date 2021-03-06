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
            routine(idx, sumupList, self, reportingList)
            

def buildReportingRules(rulesxml, settingsxml):
    reportRules = {}
    tree = bdeutil.readXMLTree(settingsxml)
    node = tree.find('Reporting/Categories')
    for element in node.getiterator('Category'):
        categoryName = element.attrib['Name']
        thisRule = ReportingRule(categoryName)
        for ruleElement in element.find('Rules').getiterator('Rule'):
            thisRule.addReportRule(ruleElement.attrib['Name'])
            # Read rule definition
            ruleDef = bdeutil.readRuleDefintiion(
                ruleElement.attrib['Name'],
                bdeutil.readXMLTree(rulesxml).find('Reporting/Rules'))
            thisRule.addReportRoutine(ruleDef.routine)
            # Read any variables
            bdeutil.readRuleVars2(ruleElement, thisRule, ruleDef)
            
        # This rule is now complete
        reportRules[categoryName] = thisRule
        
    return reportRules


def rule_None(idx, sumupList, reportRule, reportingList):
    theSum = sumupList[idx]
    if theSum.reporting is not None:
        return 
    
    reporting = BdeReporting()
    
    reporting.addSumup(theSum)
    reportingList.add(reporting)
    return 


def rule_Concatenate(idx, sumupList, reportRule, reportingList):
    theSum = sumupList[idx]
    if theSum.reporting is not None:
        return 
    
    reporting = BdeReporting()
    
    duration = theSum.calculateDuration()
    impressionTotal = theSum.calculateImpressionTotal()
    
    SIG_DURATION = reportRule.getattr('SIG_DURATION')
    if SIG_DURATION is None:
        SIG_DURATION = 0.08333
    SIG_IMPCOUNT = reportRule.getattr('SIG_IMPCOUNT')
    if SIG_IMPCOUNT is None:
        SIG_IMPCOUNT = 20
    
    if duration > SIG_DURATION and impressionTotal > SIG_IMPCOUNT:
        reporting.addSumup(theSum)
        reportingList.add(reporting)
        return 
    
    if idx == 0 or idx == len(sumupList)-1:
        reporting.addSumup(theSum)
        reportingList.add(reporting)
        return 
    
    sumTerminatedByFirstLine = theSum.getFirstLine().getTerminatedSumups()
    if sumTerminatedByFirstLine == []:
        reporting.addSumup(theSum)
        reportingList.add(reporting)
        return 
    
    sumStartedByLastLine = theSum.getLastLine().getStartedSumups()
    if sumStartedByLastLine == []:
        reporting.addSumup(theSum)
        reportingList.add(reporting)
        return 
    
    preSum, postSum = bdeutil.getConcatenatableSumup(sumTerminatedByFirstLine, sumStartedByLastLine)
    
    if preSum == [] or postSum == []:
        reporting.addSumup(theSum)
        reportingList.add(reporting)
        return 
    
    if len(preSum) != 1 or len(postSum) != 1:
        raise BdeException, 'More than one concatenation candidates found.'
    
    preSum = preSum[0]
    postSum = postSum[0]
    
    if postSum.reporting is not None:
        raise BdeException, 'Sumup is already assigned to another reporting.'
    
    if preSum.reporting is None:
        # This means the preSum could be a sumup that is not required for report, e.g. JobEnd
        #raise BdeException, 'Sumup does not belong to any reporting.'
        return 
    
    # Concatenate
    preSum.reporting.addSumup(postSum)
    
    return 
    
    
def rule_MergeAdjacent(idx, sumupList, reportRule, reportingList):
    theSum = sumupList[idx]
    if theSum.reporting is None:
        return
    
    reporting = theSum.reporting
    idx = reportingList.index(reporting)
    
    if idx == 0:
        return
    
    preReporting = reportingList[idx-1]
    
    if preReporting.getName() != reporting.getName():
        return
    
    # Merge this reporting to the previous reporting
    preReporting.merge(reporting)
    # Delete this reporting since it is now merged
    reportingList.remove(reporting)
    
    
def rule_Convert(idx, sumupList, reportRule, reportingList):
    '''
    Convert a Sumup from one category to another. The behavior can be fine
    tuned by providing test conditions.
    To make sense, the conversion has to be done as the first step as a
    report processing.
    '''
    theSum = sumupList[idx]
    # This sumup must not be processed to any reporting before conversion
    if theSum.reporting is not None:
        return 
    
    onlycodes = reportRule.getattr('onlycodes')
    
    conditional = True
    
    if onlycodes is not None:
        for line in theSum.lines:
            if line.getActivityCode() not in onlycodes:
                conditional = False
                break
    
    # Convert the sumup category            
    if conditional: # If the condition is met
        theSum.name = reportRule.getattr('to_sumup')
    else: # If the condition is not met, we convert to else_sumup or remain unchanged.
        name = reportRule.getattr('else_sumup')
        if name is not None:
            theSum.name = name
    
    

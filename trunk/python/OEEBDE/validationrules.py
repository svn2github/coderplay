#!/usr/bin/env python

import datetime
import bdeutil

class ValidationRule(object):

    def __init__(self, name):
        self.name = name
        self.routine = None
    
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
        
    def setValidationRoutine(self, validationRoutine):
        self.routine = validationRoutine
        
    def action(self, cursor, errorlog):
        code, lineNumber = self.routine(cursor)
        if lineNumber != []:
            errorlog.add(code, lineNumber)
            

# Build the validation rules dictionary, which contains the validation rule objects
def buildValidationRules(rulesxml, settingsxml):
    validationRules = {}
    # Read the XML file for validation settings
    tree = bdeutil.readXMLTree(settingsxml)
    node = tree.find('Validations/Action')
    for ruleElement in node.getiterator('Rule'):
        ruleName = ruleElement.attrib['Name']
        # create the rule object
        thisRule = ValidationRule(ruleName)
        # get any additional variables
        bdeutil.readRuleVars(ruleElement, thisRule)
        # Set the routine by reading the rules xml
        thisRule.routine = bdeutil.readRuleRoutine(ruleElement.attrib['Name'],
                                                   bdeutil.readXMLTree(rulesxml).find('Validations/Rules'))
        # Fill the rule dictionary
        validationRules[ruleName] = thisRule
        
    return validationRules
            



# Data validation rules 
def rule_1(cursor):
    """
    RecordID not in master table
    """
    sql = """SELECT b.ROWID, b.* FROM bdefile b 
        LEFT OUTER JOIN recordcode r ON b.f1=r.code WHERE code IS NULL
        """
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_2(cursor):
    """
    EquipmentID not in master table
    """
    sql = """
        SELECT b.* FROM bdeview b 
        LEFT OUTER JOIN equipcode ON CAST(f6 AS INTEGER)=code 
        WHERE code IS NULL
        """
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_3(cursor):
    """
    ActivityCode not in Master table
    """
    sql = """
        SELECT b.* FROM bdeview b LEFT OUTER JOIN activitycode ON f7=code 
        WHERE code IS NULL
        """
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_5(cursor):
    """
    First significant ActivityCode in file has a zero Job ID
    """
    sql = """
        SELECT b.* FROM bdeview b 
        WHERE f5='0' 
        AND rowintable=(SELECT rowintable FROM bdeview WHERE f7<>'@17' LIMIT 1)
        """
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_6(cursor):
    """
    First significant ActivityCode not MR or @95
    """
    sql = """
        SELECT b.* FROM bdeview b 
        WHERE rowintable=(SELECT rowintable FROM bdeview WHERE f7<>'@17' LIMIT 1) 
        AND f7 NOT IN (SELECT code FROM activitycode WHERE item IN ('@95','MR'))
        """
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_8(cursor):
    """
    EquipmentID not consistent for all significant rows
    """
    sql = """
        SELECT * FROM bdeview WHERE f6 NOT IN (SELECT f6 FROM bdeview LIMIT 1)
        """
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_9(cursor):
    """
    TimeStamp is less than the prior record
    """
    sql = """
        SELECT b1.ROWID, b1.* FROM bdefile b1 
        JOIN bdefile b2 ON b1.ROWID=b2.ROWID-1 
        WHERE CAST(b1.f2 AS INTEGER) > CAST(b2.f2 AS INTEGER)
        """
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_10(cursor):
    """
    TimeStamp is in the future
    """
    now = bdeutil.convertDateTimeToField2(datetime.datetime.now())
    sql = "SELECT ROWID, * FROM bdefile WHERE CAST(f2 AS INTEGER)> %d" % now
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_12(cursor):
    """
    Row ImpressionTotal is less than the prior record
    """
    sql = """
        SELECT b1.* FROM bdeview b1 
        JOIN bdeview b2 ON b1.rowintable=b2.rowintable-1 
        WHERE CAST(b1.f11 AS INTEGER) > CAST(b2.f11 AS INTEGER)
        """
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_14(cursor):
    """
    Row ImpressionTotal not in range of 1m - 999m
    """
    sql = """
        SELECT * FROM bdeview 
        WHERE CAST(f11 AS INTEGER)<1000000 OR CAST(f11 AS INTEGER)>999000000
        """
    lines = cursor.execute(sql).fetchall()
    return getRuleCode(), getLineIndex(lines)

def rule_15(cursor):
    """
    File contains no @95
    """
    sql = "SELECT * FROM bdeview WHERE f7='@95'"
    lines = cursor.execute(sql).fetchall()
    if lines == []: # fail
        return getRuleCode(), [None]
    else:
        return getRuleCode(), []


def getRuleCode():
    ruleName = bdeutil.whosdaddy()
    rnlist = ruleName.split('_')
    return int(rnlist[len(rnlist)-1])
    
def getLineIndex(lines):
    lineNumber = []
    for line in lines:
        lineNumber.append(int(line[0]))
    return lineNumber
        
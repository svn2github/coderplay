#!/usr/bin/env python

import datetime
import bdeutil

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
    lineIndex = []
    for line in lines:
        lineIndex.append(int(line[0])-1)
    return lineIndex
        
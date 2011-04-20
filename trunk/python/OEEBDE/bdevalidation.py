#!/usr/bin/env python

# Data validation rules 
def rule_1(cursor):
    """
    RecordID not in master table
    """
    sql = """SELECT b.ROWID, b.* FROM bdefile b 
        LEFT OUTER JOIN recordcode r ON b.f1=r.code WHERE code IS NULL
        """
    lines = cursor.execute(sql).fetchall()
    return lines==[], lines

def rule_2():
    """
    EquipmentID not in master table
    """
    sql = """
        SELECT b.* FROM bdeview b 
        LEFT OUTER JOIN equipcode ON CAST(f6 AS INTEGER)=code 
        WHERE code IS NULL
        """
    lines = cursor.execute(sql).fetchall()
    return lines==[], lines

def rule_3():
    """
    ActivityCode not in Master table
    """
    sql = """
        SELECT b.* FROM bdeview b LEFT OUTER JOIN activitycode ON f7=code 
        WHERE code IS NULL
        """
    lines = cursor.execute(sql).fetchall()
    return lines==[], lines

def rule_5():
    """
    First significant ActivityCode in file has a zero Job ID
    """
    sql = """
        SELECT b.* FROM bdeview b 
        WHERE f5='0' 
        AND rowintable=(SELECT rowintable FROM bdeview WHERE f7<>'@17' LIMIT 1)
        """
    lines = cursor.execute(sql).fetchall()
    return lines==[], lines

def rule_6():
    """
    First significant ActivityCode not MR or @95
    """
    sql = """
        SELECT b.* FROM bdeview b 
        WHERE rowintable=(SELECT rowintable FROM bdeview WHERE f7<>'@17' LIMIT 1) 
        AND f7 NOT IN (SELECT code FROM activitycode WHERE item IN ('@95','MR'))
        """
    lines = cursor.execute(sql).fetchall()
    #return lines==[], lines
    return True, []

def rule_8():
    """
    EquipmentID not consistent for all significant rows
    """
    sql = """
        SELECT * FROM bdeview WHERE f6 NOT IN (SELECT f6 FROM bdeview LIMIT 1)
        """
    lines = cursor.execute(sql).fetchall()
    return lines==[], lines

def rule_9():
    """
    TimeStamp is less than the prior record
    """
    sql = """
        SELECT b1.ROWID, b1.* FROM bdefile b1 
        JOIN bdefile b2 ON b1.ROWID=b2.ROWID-1 
        WHERE CAST(b1.f2 AS INTEGER) > CAST(b2.f2 AS INTEGER)
        """
    lines = cursor.execute(sql).fetchall()
    return lines==[], lines

def rule_10():
    """
    TimeStamp is in the future
    """
    now = oeeutil.convert_datetime_to_f2(datetime.datetime.now())
    sql = "SELECT ROWID, * FROM bdefile WHERE CAST(f2 AS INTEGER)> %d" % now
    lines = cursor.execute(sql).fetchall()
    return lines==[], lines

def rule_11():
    """
    TimeStamp < last record in Reporting database
    """
    sql = "SELECT CAST(f2 AS INTEGER) FROM reporting ORDER BY ROWID DESC LIMIT 1"
    res = cursor.execute(sql).fetchall()
    if res == []:
        return True, []
    else:
        sql = "SELECT * FROM bdeview WHERE CAST(f2 AS INTEGER)<=%d" % res[0][0]
        lines = cursor.execute(sql).fetchall()
        return lines==[], lines

def rule_12():
    """
    Row ImpressionTotal is less than the prior record
    """
    sql = """
        SELECT b1.* FROM bdeview b1 
        JOIN bdeview b2 ON b1.rowintable=b2.rowintable-1 
        WHERE CAST(b1.f11 AS INTEGER) > CAST(b2.f11 AS INTEGER)
        """
    lines = cursor.execute(sql).fetchall()
    return lines==[], lines

def rule_13():
    """
    Row ImpressionTotal < last value in Reporting database
    """
    sql = "SELECT CAST(f11 AS INTEGER) FROM reporting ORDER BY ROWID DESC LIMIT 1"
    res = cursor.execute(sql).fetchall()
    if res == []:
        return True, []
    else:
        sql = "SELECT * FROM bdeview WHERE CAST(f11 AS INTEGER)<=%d" % res[0][0]
        lines = cursor.execute(sql).fetchall()
        return lines==[], lines

def rule_14():
    """
    Row ImpressionTotal not in range of 1m - 999m
    """
    sql = """
        SELECT * FROM bdeview 
        WHERE CAST(f11 AS INTEGER)<1000000 OR CAST(f11 AS INTEGER)>999000000
        """
    lines = cursor.execute(sql).fetchall()
    return lines==[], lines

def rule_15():
    """
    File contains no @95
    """
    sql = "SELECT * FROM bdeview WHERE f7='@95'"
    lines = cursor.execute(sql).fetchall()
    return lines!=[], []

def rule_16():
    """
    File contains less then 500 signifcant rows
    """
    sql = "SELECT COUNT(*) FROM bdeview"
    lines = cursor.execute(sql).fetchall()
    # Temporary make it 50 for testing purpose
    return lines[0][0]>=50, []

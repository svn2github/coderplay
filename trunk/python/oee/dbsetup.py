#!/usr/bin/env python

import sys
import csv
import oeeutil

try:
    import pysqlite2.dbapi2 as lite
except ImportError:
    import sqlite3.dbapi2 as lite

def setup_reporting_table(dbname='oeebde.db'):
    """
    Create the main reporting table in the database.
    Nothing will be done if it is already in the database.
    """
    sys.stdout.write("Building TABLE reporting ...")
    # Connect to the database
    conn = lite.connect(dbname)
    c = conn.cursor()
    c.execute(oeeutil.sql_create_reporting_table)

    # finalize the operation
    conn.commit()
    c.close()
    conn.close()

    print "SUCCEEDED"



def setup_error_code(dbname='oeebde.db', filename='errorcode'):
    """
    Create and populate the errorcode table in the dababase.
    """
    
    # Read the error codes from file
    errorcode = []
    sys.stdout.write("Building TABLE errorcode ... ")
    f = open(filename, "r")
    lines = f.readlines()
    for line in lines:
        code, description = (line[:4], line[4:])
        errorcode += [(int(code.strip()), description.strip())]
    
    # Connect to the database
    conn = lite.connect(dbname)
    c = conn.cursor()
    sql_create_errorcode_table="""
    CREATE TABLE IF NOT EXISTS errorcode(
    code INTEGER NOT NULL PRIMARY KEY UNIQUE,
    description VARCHAR(255))
    """

    # create the table
    c.execute(sql_create_errorcode_table)

    # delete anything in the table
    c.execute('DELETE FROM errorcode')

    for item in errorcode:
        c.execute('INSERT INTO errorcode VALUES (?,?)',item)

    # finalize the operation
    conn.commit()
    c.close()
    conn.close()

    print "SUCCEEDED"


def setup_equipment_code(dbname='oeebde.db', filename='equipcode'):
    """
    Create and populate the equipment code table in the database.
    """
    # Read the equipment code from file
    equipcode = []
    sys.stdout.write("Building TABLE equipcode ... ")
    f = csv.reader(open(filename))

    # Connect to the database
    conn = lite.connect(dbname)
    c = conn.cursor()
    sql_create_equipcode_table="""
    CREATE TABLE IF NOT EXISTS equipcode(
    code INTEGER NOT NULL PRIMARY KEY UNIQUE,
    description VARCHAR(255))
    """
    c.execute(sql_create_equipcode_table)

    # Insert into table
    c.execute('DELETE FROM equipcode')
    for line in f:
        c.execute('INSERT INTO equipcode VALUES(?,?)', tuple(line))

    # finalize the operation
    conn.commit()
    c.close()
    conn.close()

    print "SUCCEEDED"

def setup_activity_code(dbname='oeebde.db', filename='activitycode'):
    """
    Create and populate the activity code table in the database.
    """
    # Read the activity code from file
    activitycode = []
    sys.stdout.write("Building TABLE activitycode ... ")
    f = csv.reader(open(filename),delimiter="\t")

    # Connect to the database
    conn = lite.connect(dbname)
    c = conn.cursor()
    sql_create_activitycode_table="""
    CREATE TABLE IF NOT EXISTS activitycode(
    code VARCHAR(10), 
    item VARCHAR(20), 
    oeepoint VARCHAR(50),
    description VARCHAR(255))
    """
    c.execute(sql_create_activitycode_table)

    # Insert into table
    c.execute('DELETE FROM activitycode')
    for line in f:
        c.execute('INSERT INTO activitycode VALUES(?,?,?,?)', tuple(line))

    # finalize the operation
    conn.commit()
    c.close()
    conn.close()

    print "SUCCEEDED"


if __name__ == "__main__":
    #setup_error_code()
    #setup_equipment_code()
    #setup_activity_code()
    setup_reporting_table()



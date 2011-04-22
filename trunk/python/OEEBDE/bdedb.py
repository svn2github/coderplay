#!/usr/bin/env python

import csv
import sqlite3.dbapi2 as lite
import equipmentcode
import activitycode


class BdeDB(object):
    def __init__(self):
        """
        Connect to a database and return the connection and cursor objects.
        """
        self.conn = lite.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.buildRecordCodeTable()
        self.buildEquipmentCodeTable()
        self.buildActivityCodeTable()
        
    
    def buildRecordCodeTable(self):
        """
        Create and populate the Record Code table in the database.
        """
        # Build the table
        sql = """
        CREATE TABLE IF NOT EXISTS RecordCode(
        id INTEGER PRIMARY KEY,
        code VARCHAR(10))
        """
        self.cursor.execute(sql)
        
        # Insert into table
        self.cursor.execute('DELETE FROM RecordCode')
        self.cursor.execute("INSERT INTO RecordCode (code) VALUES ('REC001')")
        self.cursor.execute("INSERT INTO RecordCode (code) VALUES ('REC011')")
        self.cursor.execute("INSERT INTO RecordCode (code) VALUES ('REC020')")
    
        # finalize the operation
        self.conn.commit()
        
        return True
    
    def buildEquipmentCodeTable(self):
        """
        Create and populate the equipment code table in the database.
        """
        # Build the table
        sql_create_equipcode_table="""
        CREATE TABLE IF NOT EXISTS equipcode(
        code INTEGER NOT NULL PRIMARY KEY UNIQUE,
        description VARCHAR(255))
        """
        self.cursor.execute(sql_create_equipcode_table)
    
        # Insert into table
        self.cursor.execute('DELETE FROM equipcode')
        # Read the equipment code from file
        keys = equipmentcode.lookupTable.keys()
        for key in keys:
            self.cursor.execute('INSERT INTO equipcode VALUES(?,?)', (key, equipmentcode.lookupTable[key]))
    
        # finalize the operation
        self.conn.commit()
        
        return True
    
    def buildActivityCodeTable(self):
        """
        Create and populate the activity code table in the database.
        """
    
        # Connect to the database
        sql_create_activitycode_table="""
        CREATE TABLE IF NOT EXISTS activitycode(
        code VARCHAR(10), 
        item VARCHAR(20), 
        oeepoint VARCHAR(50),
        description VARCHAR(255))
        """
        self.cursor.execute(sql_create_activitycode_table)
    
        # Insert into table
        self.cursor.execute('DELETE FROM activitycode')
        keys = activitycode.lookupTable.keys()
        for key in keys:
            value = [key]
            value += activitycode.lookupTable[key]
            self.cursor.execute('INSERT INTO activitycode VALUES(?,?,?,?)', tuple(value))
    
        # finalize the operation
        self.conn.commit()
    
        return True
        
    def __del__(self):
        self.cursor.close()
        self.conn.close()
    
    def loaddata(self, file):
        """
        Establish the connection to the database and load content list into a table.
        """
        # Read the content using csv reader
        lines = csv.reader(open(file),delimiter="\t")

        content = []
        # Store the content in the class
        for line in lines:
            content += [tuple(line)]
            
        # create the bdefile table to 
        sql_create_bdefile_table="""
        CREATE TABLE IF NOT EXISTS bdefile(
        f1 varchar(10),
        f2 varchar(50),
        f3 varchar(50),
        f4 varchar(50),
        f5 varchar(50),
        f6 varchar(50),
        f7 varchar(50),
        f8 varchar(50),
        f9 varchar(50),
        f10 varchar(50),
        f11 varchar(50),
        f12 varchar(50),
        f13 varchar(50),
        f14 varchar(50));
        """

        self.cursor.execute(sql_create_bdefile_table)
        # Delete any previous records
        self.cursor.execute('DELETE FROM bdefile')
        # hold the content for analysis
        for item in content:
            self.cursor.execute('INSERT INTO bdefile VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', item)
            
        
        sql_create_bdefile_view="""
        DROP VIEW IF EXISTS bdeview;

        CREATE VIEW bdeview AS SELECT ROWID AS rowintable, * FROM bdefile WHERE f1='REC020';
        """
        
        self.cursor.executescript(sql_create_bdefile_view)
        self.conn.commit()


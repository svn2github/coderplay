#!/usr/bin/env python

import sys
import csv
import datetime
import pdb
import oeeutil

try:
    import pysqlite2.dbapi2 as lite
except ImportError:
    import sqlite3.dbapi2 as lite


class oeebde():
    """
    This class is a processor for the OEE *.bde input file.
    It reads the bde file and maintain its content with a list. This list is going to
    be the main source of futher processes, including displaying in a GUI, validation
    rules. The general process of the data validation is as follows:
    1. Invoke SQLite and create temporary tables to store the content of the list.
    2. Run data validation runs and report any errors found.
    3. Users modify the list until the validation runs are successful. Ideally, the 
       modification process should be done interactively via a GUI. But other ways are
       also acceptable, including via command line operations, or modifiy the source
       bde file independantly and reload it.
    4. The validated list can be uploaded to the main table.
    5. Users should be able to save the list as bde files at any point during the 
       process.
    """

    def __init__(self, bdefilename=None):
        """
        Initialize the class and read the bde file is it is provided.
        """
        self.content = []
        self.dbname = 'oeebde.db'
        self.recordcode = 'recordcode'
        self.nfilelines = 0
        if bdefilename is not None:
            self.bdefilename = bdefilename
            self.readfile(bdefilename)

    def readfile(self, bdefilename):
        """
        Read the content of a bde file and store it in a list variable.
        """
        # Read the content using csv reader
        f = csv.reader(open(bdefilename),delimiter="\t")

        # Store the content in the class
        success = True
        for line in f:
            # The input has to be exactly 14 fields per row
            if len(line) != 14:
                success = False
            self.content += [tuple(line)]

        self.nfilelines = f.line_num

        return success

    def connect_db(self, dbname=None):
        """
        Connect to a database and return the connection and cursor objects.
        """
        if dbname is None:
            conn = lite.connect(':memory')
        else:
            conn = lite.connect(dbname)
        c = conn.cursor()

        #
        self.code_JobEnd = ['@97']
        #
        lines = c.execute("SELECT code FROM activitycode WHERE item IN ('MR', '@95')")
        self.code_MR = [item[0] for item in lines]
        #
        lines = c.execute("SELECT code FROM activitycode WHERE item='Prod'")
        self.code_Prod = [item[0] for item in lines]
        #
        lines = c.execute("SELECT code, oeepoint FROM activitycode WHERE item='W-up'")
        lookup = {'ON': 1, 'OFF': -1, '': 0}
        self.code_Wup = dict([(item[0], lookup[item[1]]) for item in lines])
        #
        lines = c.execute("SELECT code FROM activitycode WHERE oeepoint='Process'")
        self.code_Process = [item[0] for item in lines]
        #
        lines = c.execute("SELECT code FROM activitycode WHERE oeepoint LIKE 'Maintenance%'")
        self.code_Maintenance = [item[0] for item in lines]

        return conn, c

    def disconnect_db(self):
        self.c.close()
        self.conn.close()

    def loaddata(self):
        """
        Establish the connection to the database and load content list into a table.
        """
        # Connect to the db
        self.conn, self.c = self.connect_db(self.dbname)
        # create the bdefile table to 
        self.c.execute(oeeutil.sql_create_bdefile_table)
        # Delete any previous records
        self.c.execute('DELETE FROM bdefile')
        # hold the content for analysis
        for item in self.content:
            self.c.execute('INSERT INTO bdefile VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', item)
        self.c.executescript(oeeutil.sql_create_bdefile_view)
        self.conn.commit()


    def data_validation(self):
        """
        This function introspect the class's validation methods and execute them.
        The validation method returns a tuple of two elements. The first element is a 
        boolean flag indicating whether the validation is successful. The second element
        is a list of the line number and the content of the line where validation fails.
        The list is empty is validation is successful.
        The validation run stops when any of the check fails.
        """
        allattr = dir(oeebde)
        idx = [ii for ii, attr in enumerate(allattr) if "validate_oee_error_" in attr]
        vfunclist = []
        for ii in idx:
            vfunclist += [allattr[ii]]

        errorcodes = []
        for vfunc in vfunclist:
            errorcodes += [int(vfunc.split('_')[3])]

        errorcodes.sort()

        for code in errorcodes:
            sys.stdout.write("Checking validation rule %d ... " % code)
            success, lines = (eval('self.validate_oee_error_'+str(code)))()
            if success:
                print "PASSED"
            else:
                print self.get_error_description(code)
                for line in lines:
                    print "  line %d: %s" % (line[0], ",".join(line[1:]))
                return False

        return True


    # Data validation rules 
    def validate_oee_error_1(self):
        """
        RecordID not in master table
        """
        sql = """SELECT b.ROWID, b.* FROM bdefile b 
            LEFT OUTER JOIN recordcode r ON b.f1=r.code WHERE code IS NULL
            """
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_2(self):
        """
        EquipmentID not in master table
        """
        sql = """
            SELECT b.* FROM bdeview b 
            LEFT OUTER JOIN equipcode ON CAST(f6 AS INTEGER)=code 
            WHERE code IS NULL
            """
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_3(self):
        """
        ActivityCode not in Master table
        """
        sql = """
            SELECT b.* FROM bdeview b LEFT OUTER JOIN activitycode ON f7=code 
            WHERE code IS NULL
            """
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_5(self):
        """
        First significant ActivityCode in file has a zero Job ID
        """
        sql = """
            SELECT b.* FROM bdeview b 
            WHERE f5='0' 
            AND rowintable=(SELECT rowintable FROM bdeview WHERE f7<>'@17' LIMIT 1)
            """
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_6(self):
        """
        First significant ActivityCode not MR or @95
        """
        sql = """
            SELECT b.* FROM bdeview b 
            WHERE rowintable=(SELECT rowintable FROM bdeview WHERE f7<>'@17' LIMIT 1) 
            AND f7 NOT IN (SELECT code FROM activitycode WHERE item IN ('@95','MR'))
            """
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_8(self):
        """
        EquipmentID not consistent for all significant rows
        """
        sql = """
            SELECT * FROM bdeview WHERE f6 NOT IN (SELECT f6 FROM bdeview LIMIT 1)
            """
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_9(self):
        """
        TimeStamp is less than the prior record
        """
        sql = """
            SELECT b1.ROWID, b1.* FROM bdefile b1 
            JOIN bdefile b2 ON b1.ROWID=b2.ROWID-1 
            WHERE CAST(b1.f2 AS INTEGER) > CAST(b2.f2 AS INTEGER)
            """
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_10(self):
        """
        TimeStamp is in the future
        """
        now = oeeutil.convert_datetime_to_f2(datetime.datetime.now())
        sql = "SELECT ROWID, * FROM bdefile WHERE CAST(f2 AS INTEGER)> %d" % now
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_11(self):
        """
        TimeStamp < last record in Reporting database
        """
        sql = "SELECT CAST(f2 AS INTEGER) FROM reporting ORDER BY ROWID DESC LIMIT 1"
        res = self.c.execute(sql).fetchall()
        if res == []:
            return True, []
        else:
            sql = "SELECT * FROM bdeview WHERE CAST(f2 AS INTEGER)<=%d" % res[0][0]
            lines = self.c.execute(sql).fetchall()
            return lines==[], lines

    def validate_oee_error_12(self):
        """
        Row ImpressionTotal is less than the prior record
        """
        sql = """
            SELECT b1.* FROM bdeview b1 
            JOIN bdeview b2 ON b1.rowintable=b2.rowintable-1 
            WHERE CAST(b1.f11 AS INTEGER) > CAST(b2.f11 AS INTEGER)
            """
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_13(self):
        """
        Row ImpressionTotal < last value in Reporting database
        """
        sql = "SELECT CAST(f11 AS INTEGER) FROM reporting ORDER BY ROWID DESC LIMIT 1"
        res = self.c.execute(sql).fetchall()
        if res == []:
            return True, []
        else:
            sql = "SELECT * FROM bdeview WHERE CAST(f11 AS INTEGER)<=%d" % res[0][0]
            lines = self.c.execute(sql).fetchall()
            return lines==[], lines

    def validate_oee_error_14(self):
        """
        Row ImpressionTotal not in range of 1m - 999m
        """
        sql = """
            SELECT * FROM bdeview 
            WHERE CAST(f11 AS INTEGER)<1000000 OR CAST(f11 AS INTEGER)>999000000
            """
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_15(self):
        """
        File contains no @95
        """
        sql = "SELECT * FROM bdeview WHERE f7='@95'"
        lines = self.c.execute(sql).fetchall()
        return lines!=[], []

    def validate_oee_error_16(self):
        """
        File contains less then 500 signifcant rows
        """
        sql = "SELECT COUNT(*) FROM bdeview"
        lines = self.c.execute(sql).fetchall()
        return lines[0][0]>=500, []

    def get_error_description(self, code):
        """
        Retrieve and return the error description using the error code.
        """
        self.c.execute("SELECT * FROM errorcode WHERE code=%d" % code)
        return self.c.fetchone()[1]

    
    def data_sumup(self):
        primary_entries = self.code_MR + self.code_Prod + self.code_Prod \
            + self.code_JobEnd + self.code_Maintenance
        plines = [line for line in self.content if line[6] in primary_entries]

        pdb.set_trace()


if __name__ == '__main__':
    bde = oeebde()
    if not bde.readfile("good.bde"):
        print 'Error: Incorrect file format.'
        sys.exit(0)
    bde.loaddata()
    if not bde.data_validation():
        print 'Error: Data validation fails.'
        sys.exit(0)
    bde.data_sumup()





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

        self.code_JobStart = ['@95']
        self.code_JobEnd = ['@97']

        lines = c.execute("SELECT code FROM activitycode WHERE item='MR'")
        self.code_MR = [item[0] for item in lines]
        lines = c.execute("SELECT code FROM activitycode WHERE item='Prod'")
        self.code_Prod = [item[0] for item in lines]
        lines = c.execute("SELECT code, oeepoint FROM activitycode WHERE item='W-up'")
        lookup = {'ON': 1, 'OFF': -1, '': 0}
        self.code_Wup = dict([(item[0], lookup[item[1]]) for item in lines])
        lines = c.execute("SELECT code FROM activitycode WHERE oeepoint='Process'")
        self.code_Process = [item[0] for item in lines]
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
        sql = "SELECT b.ROWID, b.* FROM bdefile b LEFT OUTER JOIN recordcode r ON b.f1=r.code WHERE code IS NULL"
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_3(self):
        now = oeeutil.convert_datetime_to_f2(datetime.datetime.now())
        sql = "SELECT ROWID, * FROM bdefile WHERE CAST(f2 AS INTEGER)> %d" % now
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_4(self):
        sql = "SELECT b1.ROWID, b1.* FROM bdefile b1 JOIN bdefile b2 ON b1.ROWID=b2.ROWID-1 WHERE CAST(b1.f2 AS INTEGER) > CAST(b2.f2 AS INTEGER)"
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_5(self):
        sql = "SELECT ROWID, * FROM bdefile WHERE ROWID=1 AND f2 IS NULL"
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_6(self):
        sql = "SELECT b.* FROM bdeview b LEFT OUTER JOIN equipcode ON CAST(f6 AS INTEGER)=code WHERE code IS NULL"
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_7(self):
        sql = "SELECT b.* FROM bdeview b LEFT OUTER JOIN activitycode ON f7=code WHERE code IS NULL"
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_8(self):
        sql = "SELECT * FROM bdeview WHERE CAST(f11 AS INTEGER)<1000000 OR CAST(f11 AS INTEGER)>999000000"
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_9(self):
        sql = "SELECT CAST(f11 AS INTEGER) FROM reporting ORDER BY ROWID DESC LIMIT 1"
        res = self.c.execute(sql).fetchall()
        if res == []:
            return True, []
        else:
            sql = "SELECT * FROM bdeview WHERE CAST(f11 AS INTEGER)<=%d" % res[0][0]
            lines = self.c.execute(sql).fetchall()
            return lines==[], lines

    def validate_oee_error_10(self):
        sql = "SELECT b1.* FROM bdeview b1 JOIN bdeview b2 ON b1.rowintable=b2.rowintable-1 WHERE CAST(b1.f11 AS INTEGER) > CAST(b2.f11 AS INTEGER)"
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_11(self):
        sql =  "SELECT * FROM bdeview WHERE f6 <> (SELECT f6 FROM bdeview LIMIT 1)"
        lines = self.c.execute(sql).fetchall()
        return lines==[], lines

    def validate_oee_error_12(self):
        """
        Make sure all activity code is valid. This seems already been done with rule 7.
        """
        return True, []

    def validate_oee_error_13(self):
        """
        A valid job start/end sequence must have a @97 as job "end" entry. It must also has
        either a @95 or MR as job "start" entry. To validate the data, we loop through all
        job "end" entry and search if there is any preceeding @95 or MR entry that is in
        between of this "end" entry and the previous "end" entry.
        Note that we only take activity code 4000 to be a valid MR entry.
        """
        # Get the end entries
        sql = "SELECT * FROM bdeview WHERE f7='@97'"
        jendlines = self.c.execute(sql).fetchall()

        jstartlines = []
        badlines = []
        # Loop through the "end" entries and search for its corresponding "start" or
        # "MR" entries
        for ee, eline in enumerate(jendlines):
            # for the 1st "end" entry, there must a "start" or "MR" precedes it
            if ee == 0:
                # Find any preceeding 'MR' or 'start'
                sql = "SELECT * FROM bdeview WHERE rowintable<%d AND f7 IN ('@95','4000')" \
                       % eline[0]
                lines = self.c.execute(sql).fetchall()
            else:
                sql = "SELECT * FROM bdeview WHERE rowintable<%d AND rowintable>%d AND f7 IN ('@95','4000')" \
                       % (eline[0], jendlines[ee-1][0])
                lines = self.c.execute(sql).fetchall()

            if lines == []:
                badlines += [eline]
            else:
                jstartlines += [lines[0]]
        
        # save them for future checks
        self.jstartlines = jstartlines
        self.jendlines = jendlines

        return badlines==[], badlines


    def validate_oee_error_14(self):
        """
        We iterate through each job start/end pair to see if any line's job number
        is different from the line where job starts.
        """
        alllines = []
        for js, je in zip(self.jstartlines, self.jendlines):
            sql = "SELECT * from bdeview WHERE rowintable>=%d AND rowintable<=%d AND f5<>(SELECT f5 from bdeview WHERE rowintable=%d)" \
                    % (js[0], je[0], js[0])
            lines = self.c.execute(sql).fetchall()
            alllines += lines
        return alllines==[], alllines

    def validate_oee_error_15(self):
        """
        Iterate through each job start/end pair to see if any MR or Prod is within.
        """
        badlines = []
        for js, je in zip(self.jstartlines, self.jendlines):
            # Check for Prod
            sql = "SELECT * from bdeview WHERE rowintable>=%d AND rowintable<=%d AND f7 IN (SELECT code FROM activitycode WHERE item='Prod')" \
                    % (js[0], je[0])
            lines = self.c.execute(sql).fetchall()
            if lines == []:
                badlines += [js]
                continue
            # Check for MR
            sql = "SELECT * FROM bdeview WHERE rowintable>=%d AND rowintable<=%d AND f7 IN (SELECT code FROM activitycode WHERE item='MR')" \
                    % (js[0], je[0])
            lines = self.c.execute(sql).fetchall()
            if lines == []:
                badlines += [js]

        return badlines==[], badlines

    def validate_oee_error_802(self):
        """
        Select the first row where activity code is not @17 and check if it is @95 or MR.
        """
        sql = "SELECT DISTINCT item FROM activitycode WHERE code=(SELECT f7 FROM bdeview WHERE f7<>'@17' LIMIT 1) AND item IN ('@95','MR')"
        lines = self.c.execute(sql).fetchall()

        if lines != []:
            return True, []
        else:
            return False, self.c.execute("SELECT * FROM bdeview WHERE f7<>'@17' LIMIT 1").fetchall()


    def validate_oee_error_803(self):
        """
        Make sure no equipment id is missing. This is already done by rule 6.
        """
        return True, []

    def validate_oee_error_804(self):
        """
        Make sure equipment id is valid. This is already done by rule 6.
        """
        return True, []

    def validate_oee_error_805(self):
        """
        REC020 entries should be more than 500 lines.
        """
        sql = "SELECT COUNT(*) FROM bdeview"
        lines = self.c.execute(sql).fetchall()

        if lines[0][0] >=500:
            return True, []
        else:
            return False, []

    def validate_oee_error_806(self):
        """
        The valid file should contain at least one @95.
        """
        sql = "SELECT * FROM bdeview WHERE f7='@95'"
        lines = self.c.execute(sql).fetchall()

        if lines != []:
            return True, []
        else:
            return False, []


    def get_error_description(self, code):
        """
        Retrieve and return the error description using the error code.
        """
        self.c.execute("SELECT * FROM errorcode WHERE code=%d" % code)
        return self.c.fetchone()[1]


    def process_content(self):
        """
        Process the records line by line.
        """

        staging = {}

        wup_state = 0
        readying = ()
        producting = ()
        washing = ()
        processing = ()
        maintening = ()
        for ii, line in enumerate(self.content):
            if line[0] == 'REC020':
                # @17 is useless, we process the next line
                if line[6] == '@17': continue

                # Looking for the job start or MR 
                if line[6] in self.code_JobStart+self.code_MR:
                    # If this MR is the found during a not ready period, 
                    # it is a valid MR 
                    if not readying: 
                        readying = (ii, line[4], 'MR')
                        staging[readying] = line
                        if producting:
                            staging[producting] = [staging[producting], line]
                            producting = ()
                        if maintening:
                            staging[maintening] = [staging[maintening], line]
                            maintening = ()

                # Looking for Prod
                if line[6] in self.code_Prod:
                    if not producting:
                        producting = (ii, line[4], 'Prod')
                        staging[producting] = line
                        if readying:
                            staging[readying] = [staging[readying], line]
                            readying = ()
                        else:
                            print "Error: Production without Make Reday"
                            print line
                            break
                        if washing:
                            staging[washing] = [staging[washing], line]
                            washing = ()
                        if processing:
                            staging[processing] = [staging[processing], line]
                            processing = ()
                        if maintening:
                            staging[maintening] = [staging[maintening], line]
                            maintening = ()

                # Looking for Job End
                if line[6] in self.code_JobEnd:
                    if not producting and not readying:
                        print "Error: Job End without either Make Ready or Production"
                        print line
                        break
                    else:
                        if readying:
                            staging[readying] = [staging[readying], line]
                            readying = ()
                        if producting:
                            staging[producting] = [staging[producting], line]
                            producting = ()
                        if washing:
                            staging[washing] = [staging[washing], line]
                            washing = ()
                        if processing:
                            staging[processing] = [staging[processing], line]
                            processing = ()
                        if maintening:
                            staging[maintening] = [staging[maintening], line]
                            maintening = ()

                # Looking for Wash up
                if line[6] in self.code_Wup:
                    wup_state += self.code_Wup[line[6]]
                    if not washing:
                        washing = (ii, line[4], 'W-up')
                        staging[washing] = line
                    else:
                        if wup_state == 0:
                            staging[washing] = [staging[washing], line]
                            washing = ()
                        
                # Looking for Process
                if line[6] in self.code_Process:
                    if not washing:
                        if not processing:
                            processing = (ii, line[4], 'Process')
                            staging[processing] = [[ii,], line]
                            if washing: 
                                staging[washing] = [staging[washing], line]
                                washing = ()
                        else:
                            if ii-1 != staging[processing][0][0]:
                                staging[processing] = [staging[processing], line]
                                processing = (ii, line[4], 'Process')
                                staging[processing] = [[ii,], line]
                            else:
                                staging[processing][0][0] = ii

                # Looking for Maintenance
                if line[6] in self.code_Maintenance:
                    maintening = (ii, line[4], 'Maintenance')
                    staging[maintening] = line

        self.staging = staging

        return staging

    # Find valid MR and Prod and calculate durations
    def calc_duration(self):

        output = []

        lastmr = -1
        lastprod = -1
        keys = staging.keys()
        keys.sort()
        for key in keys:
            if key[2] == 'MR':
                sline = self.staging[key][0]
                eline = self.staging[key][1]
                stime = oeeutil.convert_f2_to_datetime(sline[1])
                etime = oeeutil.convert_f2_to_datetime(eline[1])
                duration = (etime-stime).seconds/3600.0
                impress = int(eline[10]) - int(sline[10])
                if duration >= 5.0/60.0 and impress >= 20:
                    output.append([str(stime), sline[4], 'MR', "%.2f" % duration, impress])
                    lastmr = len(output) - 1
                else:
                    output[lastmr][3] = "%.2f" % (float(output[lastmr][3]) + duration)
                    output[lastmr][4] += impress

            if key[2] == 'Prod':
                sline = self.staging[key][0]
                eline = self.staging[key][1]
                stime = oeeutil.convert_f2_to_datetime(sline[1])
                etime = oeeutil.convert_f2_to_datetime(eline[1])
                duration = (etime-stime).seconds/3600.0
                impress = int(eline[10]) - int(sline[10])
                if duration >= 5.0/60.0 and (impress >=20 or output[lastmr][3] >=20):
                    output += [[str(stime), sline[4], 'Prod', "%.2f" % duration, impress]]
                    lastprod = len(output) - 1
                else:
                    output[lastprod][3] = "%.2f" % (float(output[lastprod][3]) + duration)
                    output[lastprod][4] += impress

        self.output = output

        return output
                



if __name__ == '__main__':
    bde = oeebde()
    if not bde.readfile("good.bde"):
        print 'Error: Incorrect file format.'
        sys.exit()
    bde.loaddata()
    if not bde.data_validation():
        print 'Error: Data validation fails.'
        sys.exit()
    staging = bde.process_content()
    output = bde.calc_duration()
    bde.disconnect_db()
    keys = staging.keys()
    keys.sort()







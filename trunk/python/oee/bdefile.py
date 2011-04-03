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


class bdefile():
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
        self.dbname = 'oeebde.db'
        self.recordcode = 'recordcode'
        self.nfilelines = 0
        if bdefilename is not None:
            self.bdefilename = bdefilename
            self.readfile(bdefilename)
        # options
        self.verbose = False
        # Variables related to sumup
        # The status code of a Sum-up to indicate whether it is currently happening
        self.sum_status = {'Preparation': 0, 'Production': 0, 'Maintenance': 0, 'Process': 0, 'W-up': 0, 'JobEnd': 0}
        # The results variables
        self.content = []
        self.sumups = {}
        self.output = {}
        self.errors = {}
        self.unsumed_lines = []
        # Constant to indicate whether a Sum-up is significant
        self.SUM_UNKNOWN = -1
        self.SUM_TRIVIAL = 0
        self.SUM_SIGNIFICANT = 1
        self.SUM_CONCATENATE = 2
        self.SUM_TRIVIAL_BUT_NEEDED = 3
        self.SUM_TRIVIAL_AND_SKIPPED = 4
        # significant duration is 5 min (convert to unit hour)
        self.SIG_DURATION = 5.0/60.0
        # significant Impreesion Count is 20
        self.SIG_IMPCOUNT = 20

    def reset(self):
        # Reset all analysis related variables
        self.content = []
        self.sumups = {}
        self.output = {}
        self.errors = {}
        self.unsumed_lines = []
        for key in self.sum_status: self.sum_status[key] = 0

    def readfile(self, bdefilename):
        """
        Read the content of a bde file and store it in a list variable.
        """
        # Reset for new file
        self.reset()

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

        # JobEnd
        self.code_JobEnd = ['@97', '@96']
        # MR include MR and @95
        lines = c.execute("SELECT code FROM activitycode WHERE item IN ('MR', '@95')")
        self.code_MR = [item[0] for item in lines]
        # Production
        lines = c.execute("SELECT code FROM activitycode WHERE item='Prod'")
        self.code_Prod = [item[0] for item in lines]
        # Wash ups
        lines = c.execute("SELECT code, oeepoint FROM activitycode WHERE item='W-up'")
        lookup = {'ON': 1, 'OFF': -1, '': 0}
        self.code_Wup = dict([(item[0], lookup[item[1]]) for item in lines])
        # production downtime, named as Process
        pd = ('Plate','Cplate','Stock','Customer','Process','Org','Dry')
        lines = c.execute("SELECT code, oeepoint FROM activitycode WHERE oeepoint IN ('%s','%s','%s','%s','%s','%s','%s')" % pd)
        self.code_Process = dict([(item[0],item[1]) for item in lines])
        # Non-Production Downtime, named as Maintenance for historical reasons
        nonpd = ('Clean-up','Maintenance-I','Maintenance-H','Training','Nowork','Breakdown','Other')
        lines = c.execute("SELECT code, oeepoint FROM activitycode WHERE oeepoint IN ('%s','%s','%s','%s','%s','%s','%s')" % nonpd)
        self.code_Maintenance = dict([(item[0],item[1]) for item in lines])

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
        print "Starting basic data validation ..."
        allattr = dir(bdefile)
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
                self.report_error(code, lines)
                return False
        
        print "Basic data validation succeeded.\n"
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
        #return lines==[], lines
        return True, []

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
        """
        Perform Sum-ups for Preparation and Production.
        The Sum-ups will be performed in two stages:
        1. Simple Sum-ups to process through all selected lines and record the start and end
           lines of the Sum-ups. The results are saved in a intermediate dictionary.
        2. Process dictionary to decide whether a Sum-up is significant or not.
          Use Preparation Sum-up for an example. If a MR entry is read and Preparation sum-up
        is not currently happening, the Preparation sum-up is triggered. The (line number,
        'Preparation', JobID, ActivityCode) tuple will be used as a dictionary key to record the
        corresponding line. But as for now, we do not know if the this Sum-up will be signifcant
        or not. So an additional status code will also be recorded to indicated that we do not
        know if the Sum-up is significant. This status code will be updated in later process
        on the dictionary to reflect the Sum-up's true nature.
        """

        print "Starting data sum-ups and advanced error checking ..."
        # Get the lines of REC020 only
        plines = [(ii+1,)+line for ii, line in enumerate(self.content) if line[0]=='REC020']

        wup_state = 0
        # Process the lines of REC020
        for line in plines:
            if line[7] in self.code_MR:
                # Trigger the Sum-up if it is not currenlty running
                self.start_sumup('Preparation', line)
                # Any other Sum-up should be ended
                self.end_sumup('Production', line)
                self.end_sumup('Maintenance', line)
                self.end_sumup('Process', line)
                if self.end_sumup('W-up', line) and wup_state!=0:
                    self.report_error(910, line)
                    wup_state = 0

            elif line[7] in self.code_Prod:
                self.start_sumup('Production', line)
                self.end_sumup('Preparation', line)
                self.end_sumup('Maintenance', line) and self.report_error(913, line)
                self.end_sumup('Process', line)
                if self.end_sumup('W-up', line) and wup_state!=0:
                    self.report_error(910, line)
                    wup_state = 0

            elif line[7] in self.code_JobEnd:
                # Job End entry triggers and end the Sum-Up
                self.start_sumup('JobEnd', line)
                self.end_sumup('JobEnd', line)
                # All Sum-Ups should be stopped by a JobEnd code
                self.end_sumup('Preparation', line)
                self.end_sumup('Production', line)
                self.end_sumup('Maintenance', line) and self.report_error(914, line)
                self.end_sumup('Process', line)
                if self.end_sumup('W-up', line) and wup_state!=0:
                    self.report_error(910, line)
                    wup_state = 0

            elif line[7] in self.code_Maintenance:
                self.start_sumup('Maintenance', line)
                self.end_sumup('Preparation', line) and self.report_error(911, line)
                self.end_sumup('Production', line) and self.report_error(912, line)
                self.end_sumup('Process', line)
                if self.end_sumup('W-up', line) and wup_state!=0:
                    self.report_error(910, line)
                    wup_state = 0

            elif line[7] in self.code_Process:
                self.start_sumup('Process', line)

            elif line[7] in self.code_Wup:
                # only take those W-up entries with ON/OFF status to be countable W-up
                if self.code_Wup[line[7]] != 0:
                    if wup_state==0:
                        self.start_sumup('W-up', line)
                    wup_state += self.code_Wup[line[7]]
                    if wup_state==0:
                        self.end_sumup('W-up', line)
            else:
                # Record any un-sumed lines
                self.unsumed_lines.append(line[0])

        # Make sure every Sum-Up is correctly finished
        for key in self.sum_status:
            if self.sum_status[key]:
                self.report_error(800, self.sumups[self.sum_status[key]][1])
                print '  %s Sum-Up started but not ended' % key
                return False

        # Primary entries are those entries that affect Preparation and Production Sum-Ups
        primary_entries = self.code_MR + self.code_Prod + self.code_JobEnd + self.code_Maintenance.keys()
        # Get keys of primary entries
        pkeys = [key for key in self.sumups.keys() if key[3] in primary_entries]
        # Sort the sumup entries 
        pkeys.sort()
        # Get minor keys
        mkeys = [key for key in self.sumups.keys() if key[3] not in primary_entries]
        mkeys.sort()

        # Error checking for sumups
        mring = False
        proding = False
        jobid = 0
        alljobid = []
        for key in pkeys:
            if key[1] == 'Preparation':
                if mring:
                    # print "Error: Preparation started before previous Preparation ends"
                    self.report_error(917, self.sumups[key][1])
                mring = True
                proding = False
                jobid = self.sumups[key][1][5]
            elif key[1] == 'Production':
                if self.sumups[key][1][5] != jobid and jobid != 0:
                    self.report_error(802, self.sumups[key][1])
                else:
                    alljobid.append(jobid)
                if proding:
                    # print "Error: Production started before previous Production ends"
                    self.report_error(918, self.sumups[key][1])
                if not mring:
                    self.report_error(801, self.sumups[key][1])
                proding = True
                mring = False
            elif key[1] in ['Maintenance', 'JobEnd']:
                mring = False
                proding = False
        
        if mring:
            # print "Warning: Preparation without Production"
            self.report_error(804)

        nonzeroid = set([line[4] for line in self.content if line[0]=='REC020'])
        badids = [badid for badid in nonzeroid.difference(alljobid) if badid!='0']
        if badids:
            thelines = []
            for theid in badids:
                idx = [line[4] for line in self.content].index(theid)
                thelines += [(idx+1,) + (self.content[idx])]
            self.report_error(803, thelines)


        # Generate output report for Primary entries 
        # Process the sumup results and update the significance
        for idx in range(len(pkeys)):
            # Do not process the concatenated lines
            if self.sumups[pkeys[idx]][0] == self.SUM_CONCATENATE: continue
            self.gen_output_for_key(pkeys, idx)

        # Generate output report for Minor entries
        for idx in range(len(mkeys)):
            self.gen_output_for_key(mkeys, idx)

        # Erorr checking for sumups with signifcance
        for key in pkeys:
            if self.sumups[key][0] == self.SUM_TRIVIAL:
                if key[1] == 'Preparation':
                    self.report_error(901, self.sumups[key][1])
                elif key[1] == 'Production':
                    self.report_error(902, self.sumups[key][1])

        return True


    def start_sumup(self, sumup_name, line):
        """
        Start a Sum-Up of the given sumup_name if it is not currenlty happening.
        """
        if not self.sum_status[sumup_name]:
            # set up the dictionary key with line number, Sum-Up name, JobID and ActivityCode
            thekey = (line[0], sumup_name, line[5], line[7])
            # record the starting line
            self.sumups[thekey] = [self.SUM_UNKNOWN, line]
            # Change the Sum-Up status
            self.sum_status[sumup_name] = thekey
            return True
        return False

    def end_sumup(self, sumup_name, line):
        """
        End a Sum-Up of the given sumup_name if it is currently happening and return True.
        If the Sum-Up is not currently happening, nothing will be done and a False is returned.
        """
        if self.sum_status[sumup_name]:
            thekey = self.sum_status[sumup_name]
            self.sumups[thekey] += [line]
            self.sum_status[sumup_name] = 0
            return True
        return False

    def report_error(self, code, lines=()):
        """
        Get the detailed error description based on the error code.
        Print out the error message and problematic lines and store them
        in the error tracking dictionary variable.
        """
        errordesc = self.get_error_description(code)

        print "%d  %s" % (code, errordesc)

        # If lines are empty, no further processing needed
        if not lines: return

        # Always process list of lines. If the lines variable is a tuple, 
        # i.e. we convert it to a single item list
        if type(lines).__name__ == 'tuple': lines = [lines,]

        for line in lines:
            # output detailed lines if verbose is on
            if self.verbose: print "  line %d: %s" % (line[0], ",".join(line[1:]))
            # record the errors in error tracking 
            if code in self.errors:
                self.errors[code] += [(line[0], self.content[line[0]-1])]
            else:
                self.errors[code] = [(line[0], self.content[line[0]-1])]

    def get_key_for_concatenate(self, thekey):
        if self.sumups[thekey][0] == self.SUM_CONCATENATE:
            # If the previous record is already concatenate to other lines
            # We search further up in the list
            newkey = self.sumups[thekey][3]
            return self.get_key_for_concatenate(newkey)
        else:
            return thekey
            
    def gen_output_for_key(self, keys, idx):

        key = keys[idx]

        sumups_line = self.sumups[key]
        sline = sumups_line[1]
        eline = sumups_line[2]
        stime = oeeutil.convert_f2_to_datetime(sline[2])
        etime = oeeutil.convert_f2_to_datetime(eline[2])
        # output inforamtion
        duration = (etime-stime).seconds/3600.
        impcount = int(eline[11]) - int(sline[11])
        lnum = sline[0]
        jobid = key[2]
        sumup_name = key[1]

        if key[1] in ['Preparation', 'Production']:
            #
            if duration>=self.SIG_DURATION and impcount>=self.SIG_IMPCOUNT:
                # The Sum-Up is signifcant
                self.sumups[key][0] = self.SUM_SIGNIFICANT
                self.output[key] = (lnum, stime, jobid, sumup_name, duration, impcount)
            else:
                # The Sum-Up is NOT significant
                self.sumups[key][0] = self.SUM_TRIVIAL
                # If the trivial Sum-Up is in middle of two Preparation or Production
                # We concatenate them
                if idx > 0 and idx < len(keys)-1:
                    prekey = keys[idx-1]
                    postkey = keys[idx+1]
                    # If they are the same category Sum-ups, we concatenate them
                    if prekey[1] == postkey[1]:
                        prekey = self.get_key_for_concatenate(prekey)
                        # Update the postkey item to indicate it is concatenated
                        self.sumups[postkey][0] = self.SUM_CONCATENATE
                        self.sumups[postkey] += [prekey]
                        # extend the ending time
                        self.sumups[prekey][2] = self.sumups[postkey][2]
                        # Update the output
                        self.gen_output_for_key(keys, keys.index(prekey))
                        self.sumups[key][0] = self.SUM_TRIVIAL_AND_SKIPPED
                    else:
                        # print 'Warning: Trivial Sum-up with nothing to concatenate.'
                        self.report_error(916, self.sumups[key][1])
                        self.sumups[key][0] = self.SUM_TRIVIAL_BUT_NEEDED
                        self.output[key] = (lnum, stime, jobid, sumup_name, duration, impcount)
                else:
                    # print 'Warning: Trivial Sum-up with nothing to concatenate.'
                    self.report_error(916, self.sumups[key][1])
                    self.sumups[key][0] = self.SUM_TRIVIAL_BUT_NEEDED
                    self.output[key] = (lnum, stime, jobid, sumup_name, duration, impcount)

        elif key[1] in ['Maintenance', 'Process', 'W-up', 'JobEnd']: # Other Sum-Ups are always significant
            self.sumups[key][0] = self.SUM_SIGNIFICANT
            if sumup_name == 'Maintenance': sumup_name = self.code_Maintenance[key[3]]
            if sumup_name == 'Process': sumup_name = self.code_Process[key[3]]
            self.output[key] = (lnum, stime, jobid, sumup_name, duration, impcount)

    def calc_idle_time(self):
        '''
        Calculate the idle time between a JobEnd and the next work cycle.
        The idle time is defined as the time difference between the JobEnd entry
        and the next work cycle entry (Preparation or Production), substract any
        other sum-ups occupied time (W-up, Maintenance), and must be
        greater than 5 minutes.
        '''
        tt = 0.0
        keys = self.output.keys()
        keys.sort()
        jobEndKeys = [thekey for thekey in keys if 'JobEnd' in thekey]
        jobEndKeys = jobEndKeys[0:len(jobEndKeys)-1]
        for key in jobEndKeys:
            idxstart = keys.index(key)
            stime = self.output[keys[idxstart]][1]
            idxend = idxstart + 1
            while not (keys[idxend][1] in ['Preparation','Production']):
                idxend += 1
            # Now we have the entry where the next work cycle starts
            etime = self.output[keys[idxend]][1]
            tot_time = (etime - stime).seconds/3600.
            for ii in range(idxstart+1, idxend):
                if keys[ii][1] in ['W-up', 'Maintenance']:
                    tot_time -= self.output[keys[ii]][4]
            # if the time is longer than 5 min:
            if tot_time >= 5.0/60.0:
                tt += tot_time
        print 'idle time ', tt, ' hours'
        

    def report_output(self, output_file=None):
        # Print to stdout or file
        if output_file is None:
            outstream = sys.stdout
        else:
            outstream = open(output_file,'w')

        # Print output
        keys = self.output.keys()
        keys.sort()
        for key in keys:
            line = list(self.output[key])
            if line[3] == 'JobEnd': continue
            if line[3] == 'Preparation': line[3]='MR'
            if line[3] == 'Production': line[3]='Prod'
            line = tuple([0,] + line)
            outstream.write("%d,%d,%s,%s,%s,%0.2f,%d\n" % line)


if __name__ == '__main__':
    import argparse

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Process a bde file and perform Sum-ups.')
    parser.add_argument('INPUT_FILE',nargs='?',default='good.bde', help='name of input bde file')
    parser.add_argument('OUTPUT_FILE',nargs='?', help='name of output file')
    parser.add_argument('-v','--verbose',action='store_true', help='print more information during running time')
    arg = parser.parse_args()
    
    # Set up the output file name
    if arg.OUTPUT_FILE is None: arg.OUTPUT_FILE = arg.INPUT_FILE.split('.')[0]+'.csv'

    # Parse the bde file
    bde = bdefile()
    bde.verbose = arg.verbose
    if not bde.readfile(arg.INPUT_FILE):
        print 'Error: Incorrect file format.'
        sys.exit(0)
    bde.loaddata()
    if not bde.data_validation():
        print 'Error: Data validation fails.'
        sys.exit(0)
    if bde.data_sumup():
        bde.report_output(output_file=arg.OUTPUT_FILE)
        bde.calc_idle_time()
        print "Run succeeded"



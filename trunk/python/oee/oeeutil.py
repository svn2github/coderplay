#!/usr/bin/env python

import datetime

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

sql_create_bdefile_view="""
DROP VIEW IF EXISTS bdeview;

CREATE VIEW bdeview AS SELECT ROWID AS rowintable, * FROM bdefile WHERE f1='REC020';
"""

sql_create_reporting_table="""
CREATE TABLE IF NOT EXISTS reporting(
f1 varchar(10),
f2 varchar(10),
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

def convert_f2_to_datetime(f2):
    """
    Convert the content in the timestamp field (f2) into the datetime object.
    """
    thistime = f2[:-2]

    return datetime.datetime.strptime(thistime, "%Y%m%d%H%M%S")


def convert_datetime_to_f2(thistime):
    return int(str(thistime)[:-4].replace('-','').replace(' ','').replace(':','').replace('.',''))

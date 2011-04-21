#!/usr/bin/env python

from bdeerrorlog import BdeErrorLog
from bdefile import BdeFile
from bdeconfig import BdeConfig
from dbsetup import BdeDB

'''
Created on 15/04/2011

@author: yang
'''

# Read the file into file object
file = BdeFile('good.bde')
file.read()
    
# Process the config file
config = BdeConfig()
config.read()

# Create the sqlite DB for data validations
# Load the file into the Database
# This creates a problem that we now have two copies of the file.
# One in the file object and this one in sqlite database.
db = BdeDB()
db.loaddata('good.bde')

# The error logger
errorlog = BdeErrorLog()

# Perform required data validations based on the config file
# Add any error into the error logger
for option in config.validationOptions:
    code, lineIndex = option.routine(db.cursor)
    for index in lineIndex:
            if index is not None:
                errorlog.add(code, file.lines[index])
            else:
                errorlog.add(code, None)

# Be nice and delete the database
del(db)

# Print any errors found
for error in errorlog.errorList:
    print error[0], ': ', error[1].getLineNumber()

# Data sum-ups



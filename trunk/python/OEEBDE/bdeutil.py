#!/usr/bin/env python

import os
import inspect
import datetime
import xml.etree.ElementTree as ET

def whoami():
    return inspect.stack()[1][3]

def whosdaddy():
    return inspect.stack()[2][3]

def convertDateTimeToField2(thistime):
    return int(str(thistime)[:-4].replace('-','').replace(' ','').replace(':','').replace('.',''))
    
def readXMLTree(file='bdesettings.xml'):
    # The XML file is assumed to be in the same directory as the source
    # file. So we build the complete path to the file based on it.
    srcdir = os.path.dirname(os.path.abspath(__file__))
    # Parse the XML file
    xmlfile = os.path.join(srcdir, file)
    tree = ET.parse(xmlfile)
    return tree
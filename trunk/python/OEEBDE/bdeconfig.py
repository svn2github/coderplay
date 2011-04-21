#!/usr/bin/env python

import os
import xml.etree.ElementTree as ET
import ConfigParser
import bdevalidation

class Option(object):
    def __init__(self, name, routine, description):
        self.name = name
        self.routine = routine
        self.description = description
        self.value = None

class BdeConfig(object):
    
    def __init__(self):
        
        self.validationOptions = []
        
        srcdir = os.path.dirname(os.path.abspath(__file__))
        xmlfile = os.path.join(srcdir, 'bdesettings.xml')
        tree = ET.parse(xmlfile)
        element = tree.find('Rules')
        dict_attributes = element.attrib
        moduleName = dict_attributes['Module']
        moduleName = __import__(moduleName)
        functionBaseName = dict_attributes['Function']
        for element in tree.getiterator('Rule'):
            code = element.find('Code').text
            name = element.find('Name').text
            description = element.find('Description').text
            self.validationOptions.append(Option(name, getattr(moduleName, functionBaseName+code), description))
            
        
        
        
        
        # Setup the available validation options.
        # This includes setting up the values (default to None),
        # the routine to run for this option (default to None),
        # and the verbose description of this option.
        #self.validationOptions.append(Option('RID', 'Record Code not in master table'))
        #self.validationOptions.append(Option('EID', 'Equipment Code not in master table'))
        #self.validationOptions.append(Option('AID', 'Activity Code not in master table'))
        #self.validationOptions.append(Option('FAIDZeroJobID', 'First significant Activity Code has a zero Job ID'))
        #self.validationOptions.append(Option('FAIDnotMRor@95', 'First significant Activity Code not MR or @95'))
        #self.validationOptions.append(Option('EIDChanges', 'Equipment Code not consistent'))
        #self.validationOptions.append(Option('TSLess', 'Timestamp is less than the prior record'))
        #self.validationOptions.append(Option('TSFuture', 'Timestamp is in the future'))
        #self.validationOptions.append(Option('ITLess', 'Impression Total is less than the prior record'))
        #self.validationOptions.append(Option('ITOutbound', 'Impression Total not in range of 1-999 million'))
        #self.validationOptions.append(Option('No@95', 'File contains no @95'))
        #
        #rules = {'RID': bdevalidation.rule_1, \
        #         'EID': bdevalidation.rule_2, \
        #         'AID': bdevalidation.rule_3, \
        #         'FAIDZeroJobID': bdevalidation.rule_5, \
        #         'FAIDnotMRor@95': bdevalidation.rule_6, \
        #         'EIDChanges': bdevalidation.rule_8, \
        #         'TSLess': bdevalidation.rule_9, \
        #         'TSFuture': bdevalidation.rule_10, \
        #         'ITLess': bdevalidation.rule_12, \
        #         'ITOutbound': bdevalidation.rule_14, \
        #         'No@95': bdevalidation.rule_15}
        #
        #for option in self.validationOptions:
        #    option.routine = rules[option.name]
        
    def read(self, file='config.ini'):
        '''
        Read configuration file and populate the configs.
        '''
        cfgreader = ConfigParser.ConfigParser()
        cfgreader.read(file)
        options = cfgreader.options('Validations')
        for option in options:
            value = int(cfgreader.get('Validations', option))
            if value:
                value = True
            else:
                value = False
            if not self.setValidationOptionValue(option, value):
                print 'Option %s is not a valid entry.' % option
            
    def setValidationOptionValue(self, name, value):
        for option in self.validationOptions:
            if option.name.lower() == name.lower():
                option.value = value
                return True
        return False
    
    def setValidationOptionRoutine(self, name, routine):
        for option in self.validationOptions:
            if option.name.lower() == name.lower():
                option.routine = routine
                return True
        return False
    
    
    def getValidationOption(self, name):
        for option in self.validationOptions:
            if option.name.lower() == name.lower():
                return option


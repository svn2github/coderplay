#!/usr/bin/env python

import os
import ConfigParser
import bdevalidationrules
import bdeutil

class Option(object):
    def __init__(self, name, routine, description):
        self.name = name
        self.routine = routine
        self.description = description
        self.value = None

class BdeConfig(object):
    
    def __init__(self):
        
        # Setup the available validation options by reading the configuration
        # XML file.
        # This build the validationOptions with name, description and the
        # function used to perform the corresponding actions for the options.
        self.validationOptions = []
        
        # Get the XML setting file content tree
        tree = bdeutil.readXMLTree()
        node = tree.find('Validations/Rules')
        dict_attributes = node.attrib
        moduleName = dict_attributes['Module']
        moduleName = __import__(moduleName)
        functionBaseName = dict_attributes['Function']
        # Loop to build the option list
        for element in node.getiterator('Rule'):
            code = element.find('Code').text
            name = element.find('Name').text
            description = element.find('Description').text
            self.validationOptions.append(Option(name, getattr(moduleName, functionBaseName+code), description))
            
            
    def read(self, file='config.ini'):
        '''
        Read configuration file and populate the value of the configurations.
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
        '''
        Set the value of a validation option.
        '''
        for option in self.validationOptions:
            if option.name.lower() == name.lower():
                option.value = value
                return True
        return False
    
    
    def getValidationOption(self, name):
        '''
        Get the value of a validation option.
        '''
        for option in self.validationOptions:
            if option.name.lower() == name.lower():
                return option


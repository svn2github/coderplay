#!/usr/bin/env python

import ConfigParser

class BdeConfig(object):
    
    def __init__(self, file='config.ini'):
        self.config = {}
        cfgreader = ConfigParser.ConfigParser()
        cfgreader.read(file)
        sections = cfgreader.sections()
        for section in sections:
            options = cfgreader.options(section)
            for option in options:
                value = cfgreader.get(section, option)
                self.config[option] = value
        


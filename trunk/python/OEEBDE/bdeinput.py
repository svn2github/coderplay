#!/usr/bin/env python

import csv

class BdeOption(Object):
    
    def __init__(self, file='bdeoption'):
        self.validations = {}
        lines = csv.reader(open(file, 'r'))
        
        for line in lines:
            key = line[0]
            value = line[1]
            self.validations[key] = value
        


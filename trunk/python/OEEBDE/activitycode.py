#!/usr/bin/env python

print __name__
import csv
import bdeutil

def getName(code):
    return lookupTable[str(code)][0]

def getStatus(code):
    return lookupTable[str(code)][1]
    
def getDescription(code):
    return lookupTable[str(code)][2]

def fillLookupTable(file='activitycode'):
    '''
    Build the activity lookup table
    '''
    lookupTable = {}
    lines = csv.reader(open(file, 'r'), delimiter="\t")
    for line in lines:
        code = line[0]
        value = line[1:]
        lookupTable[code] = value
    return lookupTable
    
def fillCodeOf():
    '''
    Populate the code of every category based on the settings XML file.
    '''
    codeOf = {}
    tree = bdeutil.readXMLTree()
    node = tree.find('Sumups/Categories')
    for element in node.getiterator('Category'):
        categoryName = element.attrib['Name']
        codeOf[categoryName] = []
        for memberElement in element.getiterator('Member'):
            member = memberElement.attrib['Name']
            codes = [code for code in lookupTable.keys() if getName(code) == member]
            
            # Process any additional Status requirement
            for statusElement in memberElement.getiterator('Status'):
                # Build the contains and except list
                containsStatus = []
                exceptStatus = []
                for containsElement in statusElement.getiterator('Contains'):
                    containsStatus.append(containsElement.text)
                for exceptElement in statusElement.getiterator('Except'):
                    exceptStatus.append(exceptElement.text)
                # Apply the contains and except 
                if containsStatus != []:
                    codes = [code for code in codes if getStatus(code) in containsStatus]
                if exceptStatus != []:
                    codes = [code for code in codes if getStatus(code) not in exceptStatus]
            
            # Process any additional Code requirement
            for codeElement in memberElement.getiterator('Code'):
                # Build the contains and except list
                containsCode = []
                exceptCode = []
                for containsElement in codeElement.getiterator('Contains'):
                    containsCode.append(containsElement.text)
                for exceptElement in codeElement.getiterator('Except'):
                    exceptCode.append(exceptElement.text)
                # Apply the contains and except 
                if containsCode != []:
                    codes = [code for code in codes if code in containsCode]
                if exceptCode != []:
                    codes = [code for code in codes if code not in exceptCode]
                
            # Add the codes into this category
            codeOf[categoryName].extend(codes)
            
    return codeOf
            
# The lookup table and code categories
lookupTable = fillLookupTable()
codeOf = fillCodeOf()

def findCategory(code):
    for categoryName in codeOf.keys():
        if code in codeOf[categoryName]:
            return categoryName
    return None


if __name__ == '__main__':
    print codeOf



def rule_Significant(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    # If no sumup of this category is running
    if sumupCurrent[categoryName] is None:
        # Start own sumup
        sumupCurrent[categoryName] = BdeSumup(categoryName)
        sumupCurrent[categoryName].addLine(line)
        # Terminate all others
        for tname in sumupCurrent.keys():
            if tname == categoryName:
                continue
            if sumupCurrent[tname] is not None:
                sumupCurrent[tname].addLine(line) # add the terminate line
                sumupList.add(sumupCurrent[tname])
                sumupCurrent[tname] = None
    else: # If a sumup of this category is already running
        sumupCurrent[categoryName].addLine(line)
                
        
def rule_Parallel(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    # If no sumup of this category is running
    if sumupCurrent[categoryName] is None:
        # Start own sumup
        sumupCurrent[categoryName] = BdeSumup(categoryName)
        sumupCurrent[categoryName].addLine(line)
        # Does not terminate anything
    else: # If a sumup of this category is already running
        sumupCurrent[categoryName].addLine(line)
                

def rule_Wup(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    # If no sumup of this category is running
    if sumupCurrent[categoryName] is None:
        # Special start based on status code
        if activitycode.getStatus(line.getActivityCode()) == 'ON':
            sumupCurrent[categoryName] = BdeSumup(categoryName)
            sumupCurrent[categoryName].addLine(line)
            sumupCurrent[categoryName].status += 1
    else: # If a sumup of this category is already running
        sumupCurrent[categoryName].addLine(line)
        if activitycode.getStatus(line.getActivityCode()) == 'ON':
            sumupCurrent[categoryName].status + 1
        if activitycode.getStatus(line.getActivityCode()) == 'OFF':
            sumupCurrent[categoryName].status - 1
        # Do we need now terminate the sumup based on the status
        if sumupCurrent[categoryName].status == 0:
            # special self-termination
            sumupList.add(sumupCurrent[categoryName])
            sumupCurrent[categoryName] = None
                    
def rule_SelfCycle(line, sumupRule, sumupCurrent, sumupList):
    categoryName = sumupRule.categoryName
    # If no sumup of this category is running
    if sumupCurrent[categoryName] is None:
        if line.getActivityCode() == sumupRule.startCode:
            sumupCurrent[categoryName] = BdeSumup(categoryName)
            sumupCurrent[categoryName].addLine(line)
        
    else: # If a sumup of this category is already running
        sumupCurrent[categoryName].addLine(line)
        if line.getActivityCode() == sumupRule.endCode:
            # Self-termination
            sumupList.add(sumupCurrent[categoryName])
            sumupCurrent[categoryName] = None
            
    
    
    

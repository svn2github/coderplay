#!/usr/bin/env python

"""
Solve the following integer challenge @ CodeEval

For every test case, this algorithm's efficiency class is linear with the
big value of the number of digits or 10, i.e. C = O(max(n,10)).

  The idea is to scan the given number from the right side and do an adjacent
pair comparison and do a counting sort at the same time. 
  This procedure either finds a pair where the right digit is greater than the
left digit (1) or no such pair is found (2). 
  (1) If such pair does exist, the position of the left digit is the invertIdx
(invertIdx is -1 if no such pair exist). We can now build a sorted list of the
the digits that are scanned (excluding the invert digit, which is added to the
begining of the scanned list). Scan the sorted list again to find the first
digit that is greater than the invert digit and swap the two digit. The sorted
list can now be attached to the part of the original number that is not scanned
to build the new integer.
  (2) If no such pair is found, we simply build the sorted list and then add a
zero to the begining of the sorted list. Scan the list to find the first digit
that is greater than zero and swap them. The scan list now becomes the new 
integer.

As for the programming language, this program is not a professional python code.
But it demostrates the idea.

Oct. 19, 2011
@author ywangd
"""
import sys

f = open(sys.argv[1], 'r')

# Process each line of the test cases
for line in f:
    scanlist = list(line.strip())
    l_scanlist = len(scanlist)
    if l_scanlist == 0: continue

    # counting sort (linear)
    freq = [0]*10
    invertIdx = -1
    for ii in range(l_scanlist-1,0,-1):
        rdigit = int(scanlist[ii])
        ldigit = int(scanlist[ii-1])
        freq[rdigit] += 1
        if rdigit > ldigit:
            invertIdx = ii-1
            break

    # This is executed only when no invertIdx is found to apply counting
    # sort to all digits
    if invertIdx == -1:
        freq[ldigit] += 1

    # compute the distribution
    for ii in range(1,10):
        freq[ii] += freq[ii-1] # freq is now distribution
    # build the sorted list
    sortTail = [-1]*(l_scanlist-invertIdx-1)
    for ii in range(l_scanlist-1, invertIdx, -1):
        jj = int(scanlist[ii])
        sortTail[freq[jj]-1] = scanlist[ii]
        freq[jj] -= 1

    # An invert index has been found (linear)
    if invertIdx >= 0:
        # Add the invert digit to the begining
        sortTail.insert(0, scanlist[invertIdx])
        for ii in range(1, len(sortTail)):
            if sortTail[ii] > sortTail[0]:
                sortTail[ii], sortTail[0] = sortTail[0], sortTail[ii]
                break
        # build the new integer
        newInteger = ''.join(scanlist[0:invertIdx] + sortTail)
    else:
        # No invert index has been found (linear)
        # We need add a Zero to the begining
        sortTail.insert(0, '0')
        for ii in range(1, len(sortTail)):
            if sortTail[ii] > '0':
                sortTail[ii], sortTail[0] = sortTail[0], sortTail[ii]
                break
        # build the new integer
        newInteger = ''.join(sortTail)

    print newInteger

f.close()


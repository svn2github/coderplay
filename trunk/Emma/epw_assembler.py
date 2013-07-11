import sys

''' Assemble the output from compiler into label less assembly code
'''

def assemble(linelist):

    interlist = []
    nlines = 0
    label_dict = {}

    # first pass to build label dict
    for line in linelist:
        fields = line.split()
        opstr = fields[0]
        if opstr == 'label':
            label = fields[1]
            if label_dict.has_key(label):
                print 'duplicate labels'
                sys.exit(1)
            else:
                label_dict[label] = nlines
        else:
            interlist.append(line)
            nlines += 1


    outlist = []
    for line in interlist:
        fields = line.split()
        opstr = fields[0]
        if opstr in ['jump', 'fjump']:
            label = fields[1]
            line = opstr + ' ' + str(label_dict[label])
        elif opstr == 'push' and fields[1] == 'constant':
            if fields[2].startswith('('):
                label = fields[2]
                if label_dict.has_key(label):
                    line = 'push constant ' + str(label_dict[label])

        outlist.append(line)


    return outlist





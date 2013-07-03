import sys, os
import re

class Decompiler(object):

    def __init__(self, fileStub):
        f = open(fileStub + '.vm')
        self.contents = f.readlines()
        f.close()
        self.className = fileStub
        self.indent = 0
        self.outs = open(fileStub + '.jack', 'w')


    def write(self, *args):
        self.outs.write('    '*self.indent)
        self.outs.write(str(args[0]))
        for arg in args[1:]:
            self.outs.write(' ' + str(arg))
        self.outs.write('\n')

    def decompileStatic(self):
        '''
        Scan through the file contents and find out all static variables. 
        They must be defined before any of the subroutines.
        '''
        static_variables = []
        regex = re.compile(r'.*( static [0-9]+)')
        for line in self.contents:
            matched = regex.match(line)
            if matched:
                varname = matched.groups()[0].replace(' ', '_')
                if varname not in static_variables:
                    self.write('static', 'int', varname, ';')
                    static_variables.append(varname)


    def decompileField(self):
        '''
        Scan through the file contents and find out all field variables. 
        They must be defined before any of the subroutines.
        '''
        field_variables = []
        regex = re.compile(r'.* (this [0-9]+)')
        for line in self.contents:
            matched = regex.match(line)
            if matched:
                varname = matched.groups()[0].replace(' ', '_')
                if varname not in field_variables:
                    self.write('field', 'int', varname, ';')
                    field_variables.append(varname)


    def getFuncPositions(self):
        sLines = []
        eLines = []
        iLine = 0
        while iLine < len(self.contents):
            if self.contents[iLine].startswith('function '):
                if len(sLines) > 0:
                    eLines.append(iLine-1)
                sLines.append(iLine)
            iLine += 1
        eLines.append(len(self.contents)-1)
        return zip(sLines, eLines)


    def decompileClass(self):
        self.write('class', self.className, '{')
        self.indent +=1

        self.decompileStatic()
        self.decompileField()

        # find start and end positions of all functions
        func_pos = self.getFuncPositions()

        # decompile each functions
        for sLine, eLine in func_pos:
            contents = [line.strip() for line in self.contents[sLine:eLine+1]]
            self.decompileFunction(contents)

        self.indent -=1
        self.write('}')


    def decompileFunction(self, contents):

        iLine = 0
        nLines = len(contents)
        isDecompiled = {}
        for i in range(nLines):
            isDecompiled[i] = False

        # get the function name
        line = contents[0]
        funcName = line.split()[1].split('.')[1]
        isDecompiled[0] = True

        # find out the function type (void or not)
        line = contents[nLines-2]
        if line == 'push constant 0':
            type = 'void'
            isDecompiled[nLines-2] = True
            isDecompiled[nLines-1] = True
        elif line == 'push pointer 0': # return this
            type = self.className
            isDecompiled[nLines-2] = True
            isDecompiled[nLines-1] = True
        else:
            type = 'int'

        # find out the function kind
        if self.matchLines(contents[1:], 
                [r'push constant .*', r'call Memory.alloc .*']):
            kind = 'constructor'
            # run pass 3 lines after the func def
            # push constant x
            # call Memory.alloc 1
            # pop pointer 0
            iLine = 4
        elif self.matchLines(contents[1:], 
                [r'push argument 0', r'pop pointer 0\n']):
            kind = 'method'
            # run pass 2 lines after the func def
            # push argument 0
            # pop pointer 0
            iLine = 3
        else:
            kind = 'function'
            iLine = 1
        
        max_idx = -1
        regex = re.compile(r'.* (argument [0-9]+)')
        for line in contents:
            matched = regex.match(line)
            if matched:
                idx = int(matched.groups()[0].split()[1])
                if max_idx < idx:
                    max_idx = idx

        if max_idx > -1:
            parmlist = []
            if kind == 'method':
                for ii in range(1, max_idx+1):
                    parmlist.append('int arg_' + str(ii))
            else:
                for ii in range(max_idx+1):
                    parmlist.append('int arg_' + str(ii))
            parmlist = ', '.join(parmlist)
        else:
            parmlist = ''

        self.write(kind, type, funcName, '(', parmlist, ')', '{')
        self.indent += 1

        while iLine < nLines:
            # simple let 
            if self.matchLines(contents[iLine:], [r'push .*', r'pop .*']):
                pass

            # array element let
            elif self.matchLines(contents[iLine:], 
                    ['push constant .*', 'push .*', 'add', 'push constant 14334', 
                        'pop temp 0', 'pop pointer 1', 'push temp 0', 'pop that 0']:
                pass

    
        self.indent -= 1
        self.write('}')



    def matchLines(self, contents, patternList):
        for line, pattern in zip(contents, patternList):
            if not re.compile(pattern).match(line):
                return False
        return True


    def close(self):
        self.outs.close()



def usage(prog):
    sys.stderr.write('usage: %s [file.vm]\n' % prog)
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        usage(sys.argv[0])

    if len(sys.argv) == 2: # single file as input
        arg = sys.argv[1]
        filelist = [arg]
    else:
        # search files in the directory
        filelist = []
        for file in os.listdir("."):
            if file.endswith(".vm"):
                filelist.append(file)

    # process files
    for file in filelist:
        fileStub = file[0:file.rindex('.')]
        decompiler = Decompiler(fileStub)
        decompiler.decompileClass()

        decompiler.close()






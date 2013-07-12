import sys
from epw_bytecode import *

''' The Virtual Machine.

'''

class CollectionSlice(object):

    def __init__(self, collection, *idxlist):
        self.collection = collection
        self.idxlist = idxlist[0]

    def getValue(self):
        if len(self.idxlist) == 1:
            return self.collection[self.idxlist[0]]
        elif len(self.idxlist) == 2:
            return self.collection[slice(self.idxlist[0], self.idxlist[1])]
        elif len(self.idxlist) == 3:
            return self.collection[slice(self.idxlist[0], self.idxlist[1], self.idxlist[2])]


class Undef(object):

    def __init__(self):
        pass

    def __eq__(self, other):
        if isinstance(other, Undef):
            return True
        else:
            return False

undef = Undef()

class KwArg(object):
    
    def __init__(self, name, value):
        self.name = name
        self.value = value

class ExecutionFrame(object):
    def __init__(self, codeobject, pc, env):
        self.codeobject = codeobject
        self.pc = pc
        self.env =env

class Closure(object):
    def __init__(self, codeobject, env):
        self.codeobject = codeobject
        self.env = env


class VM(object):

    def __init__(self):
        # the working stack
        self.stack = []
        # frame stack
        self.frameStack = []

        self.frame = ExecutionFrame(codeobject=None, pc=None, 
                env=self._create_top_env())


    def run(self, codeobject):

        self.frame.codeobject = codeobject
        self.frame.pc = 0


        while True:

            instr = self._get_next_instruction()

            if instr is None:
                if self._is_in_top_env():
                    break
                else:
                    raise VMError('Code object ended prematurely.')

            opcode = instr.opcode
            if opcode == OP_PUSH:
                self.stack.append(self.frame.env.getVar(
                    self.frame.codeobject.varNames[instr.args[0]]))

            elif opcode == OP_POP:
                value = self.stack.pop()
                self.frame.env.setVar(self.frame.codeobject.varNames[instr.args[0]], value)

            elif opcode == OP_PUSHC:
                self.stack.append(self.frame.codeobject.constants[instr.args[0]])

            elif opcode == OP_JUMP:
                self.frame.pc = instr.args[0]

            elif opcode == OP_FJUMP:
                predicate = self.stack.pop()
                if not predicate:
                    self.frame.pc = instr.args[0]

            elif opcode == OP_FUNCTION: 
                func_codeobject = self.frame.codeobject.constants[instr.args[0]]
                # closure is codobject and env
                closure = Closure(func_codeobject, self.frame.env)
                self.stack.append(closure)

            elif opcode == OP_KWARG:
                # make the keyword argument and push onto stack
                value = self.stack.pop()
                kwArgName = self.codeobject.constants[self.stack.pop()]
                self.stack.append(KwArg(kwArgName, value))

            elif opcode == OP_CALL: # call
                proc = self.stack.pop()
                # proc is either builtin or closure
                arglist = [self.stack.pop() for i in range(instr.args[0])]
                arglist.reverse()

                if isinstance(proc, BuiltinProc):
                    result = proc.apply(arglist)
                    if result is not None:
                        self.stack.append(result)

                elif isinstance(proc, Closure): # user-defined function
                    # trying to plug arguments into parameters
                    nkwargs = 0
                    for arg in arglist:
                        if isinstance(arg, KwArg):
                            nkwargs += 1
                    nargs = len(arglist) - nkwargs
                    argBinding = {}
                    # initialize every parameter into undefined unless
                    # provided by the call arguments. 
                    # Note that the position arguments and keyword arguments
                    # are separated into two groups with the position arguments
                    # in the 1st group.
                    for ii in range(len(proc.codeobject.parms)):
                        parmName = proc.codeobject.parms[ii]
                        if ii < nargs:
                            argBinding[parmName] = arglist[ii]
                        else:
                            argBinding[parmName] = undef
                    # Also initialize every keyword parameter as undef.
                    # Then plug the supplied values.
                    for kwParmName in proc.codeobject.kwParms:
                        argBinding[kwParmName] = undef
                    for kwarg in arglist[nargs:]:
                        argBinding[kwarg.name] = kwarg.value

                    # push the frame stack
                    self.frameStack.append(self.frame)

                    # the env inside the func 
                    callee_env = VM_Environment(argBinding, proc.env)

                    # change the current frame to the callee's frame
                    self.frame = ExecutionFrame(
                            codeobject = proc.codeobject,
                            pc = 0, 
                            env = callee_env)

                else:
                    raise VMError('Invalid object for function call.')

            elif opcode == OP_KWPARM:
                # this is the operation trying to set the default keyword parameter values
                kwParmName = self.frame.codeobject.kwParms[instr.args[0]]
                value = self.stack.pop()
                # only plug in the default value is none is supplied by the caller
                if self.frame.env.getVar(kwParmName) == undef:
                    self.frame.env.setVar(kwParmName, value)

            elif opcode == OP_RETURN:
                self.frame = self.frameStack.pop()

            elif opcode == OP_SLICE:
                idxlist = [self.stack.pop() for i in range(instr.args[0])]
                idxlist.reverse()
                collection = self.stack.pop()
                self.stack.append(CollectionSlice(collection, idxlist))

            elif opcode in [OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MOD, OP_GT, OP_GE, 
                            OP_EQ, OP_LE, OP_LT, OP_NE, OP_AND, OP_OR, OP_XOR]:

                op2 = self.stack.pop()
                if isinstance(op2, CollectionSlice):
                    op2 = op2.getValue()
                    
                op1 = self.stack.pop()
                if isinstance(op1, CollectionSlice):
                    op1 = op1.getValue()

                if opcode == OP_ADD:
                    self.stack.append(op1 + op2)

                elif opcode == OP_SUB:
                    self.stack.append(op1 - op2)

                elif opcode == OP_MUL:
                    self.stack.append(op1 * op2)

                elif opcode == OP_DIV:
                    self.stack.append(op1 / op2)

                elif opcode == OP_MOD:
                    self.stack.append(op1 % op2)

                elif opcode == OP_GT:
                    self.stack.append(1 if op1 > op2 else 0)

                elif opcode == OP_GE:
                    self.stack.append(1 if op1 >= op2 else 0)

                elif opcode == OP_EQ:
                    self.stack.append(1 if op1 == op2 else 0)

                elif opcode == OP_LE:
                    self.stack.append(1 if op1 <= op2 else 0)

                elif opcode == OP_LT:
                    self.stack.append(1 if op1 < op2 else 0)

                elif opcode == OP_NE:
                    self.stack.append(1 if op1 != op2 else 0)

                elif opcode == OP_AND:
                    self.stack.append(1 if op1 and op2 else 0)

                elif opcode == OP_OR:
                    self.stack.append(1 if op1 or op2 else 0)

                elif opcode == OP_XOR:
                    self.stack.append(1 if op1 != op2 else 0)

                elif opcode == OP_NOT:
                    op = self.stack.pop()
                    self.stack.append(1 if (not op) else 0)

            elif opcode == OP_NEG:
                op = self.stack.pop()
                if isinstance(op, CollectionSlice):
                    op = op.getValue()
                self.stack.append(-op)

            else:
                raise self.VMError('Unknown instruction.')

    def _create_top_env(self):
        top_binding = {}
        for name, func in builtin_map.items():
            top_binding[name] = BuiltinProc(name, func)
        return VM_Environment(top_binding)

    def _is_in_top_env(self):
        return True if self.frame.env.parent is None else False

    def _get_next_instruction(self):
        if self.frame.pc >= len(self.frame.codeobject.instrlist):
            return None
        else:
            instr = self.frame.codeobject.instrlist[self.frame.pc]
            self.frame.pc += 1
            return instr


class VM_Environment(object):

    def __init__(self, binding, parent=None):
        self.binding = binding
        self.parent = parent

    def getVar(self, varName):
        if self.binding.has_key(varName):
            return self.binding[varName]
        elif self.parent:
            return self.parent.getVar(varName)
        else:
            raise VMError('Undefined variable')

    def setVar(self, varName, value):
        # variable can only be set at current environment
        self.binding[varName] = value

class BuiltinProc(object):

    def __init__(self, name, proc):
        self.name = name
        self.proc = proc

    def apply(self, args):
        return self.proc(args)

def builtin_list(args):
    if len(args) == 0:
        return []
    else:
        return [0]*args[0]

def builtin_print(args):
    for arg in args:
        if isinstance(arg, CollectionSlice):
            arg = arg.getValue()
        sys.stdout.write(str(arg) + ' ')
    sys.stdout.write('\n')

def builtin_assign(args):
    lhs = args[0]
    rhs = args[1]
    if isinstance(lhs, CollectionSlice):
        if len(lhs.idxlist) == 1:
            lhs.collection[lhs.idxlist[0]] = rhs
        elif len(lhs.idxlist) == 2:
            lhs.collection[slice(lhs.idxlist[0], lhs.idxlist[1])] = rhs
        elif len(lhs.idxlist) == 3:
            lhs.collection[slice(lhs.idxlist[0], lhs.idxlist[1], lhs.idxlist[2])] = rhs
    else:
        raise VMError('Simple assignment should not call assign builtin.')


builtin_map = {
    'list':     builtin_list,
    'print':    builtin_print,
    'assign':   builtin_assign,
}


class VMError(Exception):
    pass


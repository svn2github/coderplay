// push constant 0
@0
D=A
@SP
AM=M+1
A=A-1
M=D
// pop local 0
@SP
AM=M-1
D=M
@LCL
A=M
M=D
// label LOOP_START
(null$LOOP_START)
// push argument 0
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
// push local 0
@LCL
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
// add
@SP
AM=M-1
D=M
@SP
A=M-1
M=M+D
// pop local 0
@SP
AM=M-1
D=M
@LCL
A=M
M=D
// push argument 0
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
// push constant 1
@1
D=A
@SP
AM=M+1
A=A-1
M=D
// sub
@SP
AM=M-1
D=M
@SP
A=M-1
M=M-D
// pop argument 0
@SP
AM=M-1
D=M
@ARG
A=M
M=D
// push argument 0
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
// if-goto LOOP_START
@0
D=A
@SP
A=M-1
D=M-D
@BasicLoop.0.true.eq
D;JEQ
@SP
A=M-1
M=0
@BasicLoop.0.end.eq
0;JMP
(BasicLoop.0.true.eq)
@SP
A=M-1
M=-1
(BasicLoop.0.end.eq)
@SP
AM=M-1
D=M
@null$LOOP_START
D;JEQ
// push local 0
@LCL
A=M
D=M
@SP
AM=M+1
A=A-1
M=D

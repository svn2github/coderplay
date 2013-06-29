// push argument 1
@ARG
A=M+1
D=M
@SP
AM=M+1
A=A-1
M=D
// pop pointer 1
@SP
AM=M-1
D=M
@THAT
M=D
// push constant 0
@0
D=A
@SP
AM=M+1
A=A-1
M=D
// pop that 0
@SP
AM=M-1
D=M
@THAT
A=M
M=D
// push constant 1
@1
D=A
@SP
AM=M+1
A=A-1
M=D
// pop that 1
@SP
AM=M-1
D=M
@THAT
A=M+1
M=D
// push argument 0
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
// push constant 2
@2
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
// label MAIN_LOOP_START
(null$MAIN_LOOP_START)
// push argument 0
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
// if-goto COMPUTE_ELEMENT
@0
D=A
@SP
A=M-1
D=M-D
@FibonacciSeries.0.true.eq
D;JEQ
@SP
A=M-1
M=0
@FibonacciSeries.0.end.eq
0;JMP
(FibonacciSeries.0.true.eq)
@SP
A=M-1
M=-1
(FibonacciSeries.0.end.eq)
@SP
AM=M-1
D=M
@null$COMPUTE_ELEMENT
D;JEQ
// goto END_PROGRAM
@null$END_PROGRAM
0;JMP
// label COMPUTE_ELEMENT
(null$COMPUTE_ELEMENT)
// push that 0
@THAT
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
// push that 1
@THAT
A=M+1
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
// pop that 2
@THAT
D=M
@2
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// push pointer 1
@THAT
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
// add
@SP
AM=M-1
D=M
@SP
A=M-1
M=M+D
// pop pointer 1
@SP
AM=M-1
D=M
@THAT
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
// goto MAIN_LOOP_START
@null$MAIN_LOOP_START
0;JMP
// label END_PROGRAM
(null$END_PROGRAM)

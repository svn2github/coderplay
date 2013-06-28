// push argument 1
@ARG
A=M+1
D=M
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 1
@SP
M=M-1
A=M
D=M
@THAT
M=D
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop that 0
@SP
M=M-1
A=M
D=M
@THAT
A=M
M=D
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop that 1
@SP
M=M-1
A=M
D=M
@THAT
A=M+1
M=D
// push argument 0
@ARG
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
A=M
D=A-D
@SP
A=M
M=D
@SP
M=M+1
// pop argument 0
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
// label MAIN_LOOP_START
(MAIN_LOOP_START)
// push argument 0
@ARG
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// if-goto COMPUTE_ELEMENT
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
A=M
D=A-D
@FibonacciSeries.0.true.eq
D;JEQ
D=0
@FibonacciSeries.0.end.eq
0;JMP
(FibonacciSeries.0.true.eq)
D=-1
(FibonacciSeries.0.end.eq)
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@COMPUTE_ELEMENT
D;JEQ
// goto END_PROGRAM
@END_PROGRAM
0;JMP
// label COMPUTE_ELEMENT
(COMPUTE_ELEMENT)
// push that 0
@THAT
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push that 1
@THAT
A=M+1
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
A=M
D=A+D
@SP
A=M
M=D
@SP
M=M+1
// pop that 2
@THAT
D=M
@2
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// push pointer 1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
A=M
D=A+D
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 1
@SP
M=M-1
A=M
D=M
@THAT
M=D
// push argument 0
@ARG
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
A=M
D=A-D
@SP
A=M
M=D
@SP
M=M+1
// pop argument 0
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
// goto MAIN_LOOP_START
@MAIN_LOOP_START
0;JMP
// label END_PROGRAM
(END_PROGRAM)
(FibonacciSeries.asm.end)
@FibonacciSeries.asm.end
0;JMP

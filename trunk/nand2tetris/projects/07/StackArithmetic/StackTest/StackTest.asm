// push constant 17
@17
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 17
@17
D=A
@SP
AM=M+1
A=A-1
M=D
// eq
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
@StackTest.0.true.eq
D;JEQ
@SP
A=M-1
M=0
@StackTest.0.end.eq
0;JMP
(StackTest.0.true.eq)
@SP
A=M-1
M=-1
(StackTest.0.end.eq)
// push constant 17
@17
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 16
@16
D=A
@SP
AM=M+1
A=A-1
M=D
// eq
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
@StackTest.1.true.eq
D;JEQ
@SP
A=M-1
M=0
@StackTest.1.end.eq
0;JMP
(StackTest.1.true.eq)
@SP
A=M-1
M=-1
(StackTest.1.end.eq)
// push constant 16
@16
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 17
@17
D=A
@SP
AM=M+1
A=A-1
M=D
// eq
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
@StackTest.2.true.eq
D;JEQ
@SP
A=M-1
M=0
@StackTest.2.end.eq
0;JMP
(StackTest.2.true.eq)
@SP
A=M-1
M=-1
(StackTest.2.end.eq)
// push constant 892
@892
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 891
@891
D=A
@SP
AM=M+1
A=A-1
M=D
// lt
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
@StackTest.3.true.lt
D;JLT
@SP
A=M-1
M=0
@StackTest.3.end.lt
0;JMP
(StackTest.3.true.lt)
@SP
A=M-1
M=-1
(StackTest.3.end.lt)
// push constant 891
@891
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 892
@892
D=A
@SP
AM=M+1
A=A-1
M=D
// lt
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
@StackTest.4.true.lt
D;JLT
@SP
A=M-1
M=0
@StackTest.4.end.lt
0;JMP
(StackTest.4.true.lt)
@SP
A=M-1
M=-1
(StackTest.4.end.lt)
// push constant 891
@891
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 891
@891
D=A
@SP
AM=M+1
A=A-1
M=D
// lt
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
@StackTest.5.true.lt
D;JLT
@SP
A=M-1
M=0
@StackTest.5.end.lt
0;JMP
(StackTest.5.true.lt)
@SP
A=M-1
M=-1
(StackTest.5.end.lt)
// push constant 32767
@32767
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 32766
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
// gt
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
@StackTest.6.true.gt
D;JGT
@SP
A=M-1
M=0
@StackTest.6.end.gt
0;JMP
(StackTest.6.true.gt)
@SP
A=M-1
M=-1
(StackTest.6.end.gt)
// push constant 32766
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 32767
@32767
D=A
@SP
AM=M+1
A=A-1
M=D
// gt
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
@StackTest.7.true.gt
D;JGT
@SP
A=M-1
M=0
@StackTest.7.end.gt
0;JMP
(StackTest.7.true.gt)
@SP
A=M-1
M=-1
(StackTest.7.end.gt)
// push constant 32766
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 32766
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
// gt
@SP
AM=M-1
D=M
@SP
A=M-1
D=M-D
@StackTest.8.true.gt
D;JGT
@SP
A=M-1
M=0
@StackTest.8.end.gt
0;JMP
(StackTest.8.true.gt)
@SP
A=M-1
M=-1
(StackTest.8.end.gt)
// push constant 57
@57
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 31
@31
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 53
@53
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
// push constant 112
@112
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
// neg
@SP
A=M-1
M=-M
// and
@SP
AM=M-1
D=M
@SP
A=M-1
M=D&M
// push constant 82
@82
D=A
@SP
AM=M+1
A=A-1
M=D
// or
@SP
AM=M-1
D=M
@SP
A=M-1
M=D|M
// not
@SP
A=M-1
M=!M

@256
D=A
@SP
M=D
@Sys.init$L_Return.0
D=A
@R13
M=D
@0
D=A
@R14
M=D
@Sys.init
D=A
@R15
M=D
@GLOBAL_COMMON_CALL
0;JMP
(Sys.init$L_Return.0)
(GLOBAL_COMMON_CALL)
@R13
D=M
@SP
AM=M+1
A=A-1
M=D
@LCL
D=M
@SP
AM=M+1
A=A-1
M=D
@ARG
D=M
@SP
AM=M+1
A=A-1
M=D
@THIS
D=M
@SP
AM=M+1
A=A-1
M=D
@THAT
D=M
@SP
AM=M+1
A=A-1
M=D
@SP
D=M
@R14
D=D-M
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@R15
A=M
0;JMP
(GLOBAL_COMMON_RETURN)
@LCL
D=M
@R13
M=D
@5
D=A
@R13
A=M-D
D=M
@R6
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@R13
AM=M-1
D=M
@THAT
M=D
@R13
AM=M-1
D=M
@THIS
M=D
@R13
AM=M-1
D=M
@ARG
M=D
@R13
AM=M-1
D=M
@LCL
M=D
@R6
A=M
0;JMP
// function Class1.set 0
(Class1.set)
// push argument 0
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
// pop static 0
@SP
AM=M-1
D=M
@Class1.0
M=D
// push argument 1
@ARG
A=M+1
D=M
@SP
AM=M+1
A=A-1
M=D
// pop static 1
@SP
AM=M-1
D=M
@Class1.1
M=D
// push constant 0
@0
D=A
@SP
AM=M+1
A=A-1
M=D
// return
@GLOBAL_COMMON_RETURN
0;JMP
// function Class1.get 0
(Class1.get)
// push static 0
@Class1.0
D=M
@SP
AM=M+1
A=A-1
M=D
// push static 1
@Class1.1
D=M
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
// return
@GLOBAL_COMMON_RETURN
0;JMP
// function Class2.set 0
(Class2.set)
// push argument 0
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
// pop static 0
@SP
AM=M-1
D=M
@Class2.0
M=D
// push argument 1
@ARG
A=M+1
D=M
@SP
AM=M+1
A=A-1
M=D
// pop static 1
@SP
AM=M-1
D=M
@Class2.1
M=D
// push constant 0
@0
D=A
@SP
AM=M+1
A=A-1
M=D
// return
@GLOBAL_COMMON_RETURN
0;JMP
// function Class2.get 0
(Class2.get)
// push static 0
@Class2.0
D=M
@SP
AM=M+1
A=A-1
M=D
// push static 1
@Class2.1
D=M
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
// return
@GLOBAL_COMMON_RETURN
0;JMP
// function Sys.init 0
(Sys.init)
// push constant 6
@6
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 8
@8
D=A
@SP
AM=M+1
A=A-1
M=D
// call Class1.set 2
@Class1.set$L_Return.1
D=A
@R13
M=D
@2
D=A
@R14
M=D
@Class1.set
D=A
@R15
M=D
@GLOBAL_COMMON_CALL
0;JMP
(Class1.set$L_Return.1)
// pop temp 0
@SP
AM=M-1
D=M
@5
M=D
// push constant 23
@23
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 15
@15
D=A
@SP
AM=M+1
A=A-1
M=D
// call Class2.set 2
@Class2.set$L_Return.2
D=A
@R13
M=D
@2
D=A
@R14
M=D
@Class2.set
D=A
@R15
M=D
@GLOBAL_COMMON_CALL
0;JMP
(Class2.set$L_Return.2)
// pop temp 0
@SP
AM=M-1
D=M
@5
M=D
// call Class1.get 0
@Class1.get$L_Return.3
D=A
@R13
M=D
@0
D=A
@R14
M=D
@Class1.get
D=A
@R15
M=D
@GLOBAL_COMMON_CALL
0;JMP
(Class1.get$L_Return.3)
// call Class2.get 0
@Class2.get$L_Return.4
D=A
@R13
M=D
@0
D=A
@R14
M=D
@Class2.get
D=A
@R15
M=D
@GLOBAL_COMMON_CALL
0;JMP
(Class2.get$L_Return.4)
// label WHILE
(Sys.init$WHILE)
// goto WHILE
@Sys.init$WHILE
0;JMP

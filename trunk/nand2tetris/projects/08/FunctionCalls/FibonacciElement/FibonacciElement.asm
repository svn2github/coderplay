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
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
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
// function Main.fibonacci 0
(Main.fibonacci)
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
// lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
A=M
D=A-D
@Main.0.true.lt
D;JLT
D=0
@Main.0.end.lt
0;JMP
(Main.0.true.lt)
D=-1
(Main.0.end.lt)
@SP
A=M
M=D
@SP
M=M+1
// if-goto IF_TRUE
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
@Main.1.true.eq
D;JEQ
D=0
@Main.1.end.eq
0;JMP
(Main.1.true.eq)
D=-1
(Main.1.end.eq)
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@Main.fibonacci$IF_TRUE
D;JEQ
// goto IF_FALSE
@Main.fibonacci$IF_FALSE
0;JMP
// label IF_TRUE
(Main.fibonacci$IF_TRUE)
// push argument 0
@ARG
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// return
@LCL
D=M
@R5
M=D
@5
D=A
@R5
A=M-D
D=M
@R6
M=D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@R5
A=M-1
D=M
@THAT
M=D
@R5
D=M
@2
A=D-A
D=M
@THIS
M=D
@R5
D=M
@3
A=D-A
D=M
@ARG
M=D
@R5
D=M
@4
A=D-A
D=M
@LCL
M=D
@R6
A=M
0;JMP
// label IF_FALSE
(Main.fibonacci$IF_FALSE)
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
// call Main.fibonacci 1
@Main.fibonacci$L_Return.1
D=A
@R13
M=D
@1
D=A
@R14
M=D
@Main.fibonacci
D=A
@R15
M=D
@GLOBAL_COMMON_CALL
0;JMP
(Main.fibonacci$L_Return.1)
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
// call Main.fibonacci 1
@Main.fibonacci$L_Return.2
D=A
@R13
M=D
@1
D=A
@R14
M=D
@Main.fibonacci
D=A
@R15
M=D
@GLOBAL_COMMON_CALL
0;JMP
(Main.fibonacci$L_Return.2)
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
// return
@LCL
D=M
@R5
M=D
@5
D=A
@R5
A=M-D
D=M
@R6
M=D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@R5
A=M-1
D=M
@THAT
M=D
@R5
D=M
@2
A=D-A
D=M
@THIS
M=D
@R5
D=M
@3
A=D-A
D=M
@ARG
M=D
@R5
D=M
@4
A=D-A
D=M
@LCL
M=D
@R6
A=M
0;JMP
// function Sys.init 0
(Sys.init)
// push constant 4
@4
D=A
@SP
A=M
M=D
@SP
M=M+1
// call Main.fibonacci 1
@Main.fibonacci$L_Return.3
D=A
@R13
M=D
@1
D=A
@R14
M=D
@Main.fibonacci
D=A
@R15
M=D
@GLOBAL_COMMON_CALL
0;JMP
(Main.fibonacci$L_Return.3)
// label WHILE
(Sys.init$WHILE)
// goto WHILE
@Sys.init$WHILE
0;JMP

@256
D=A
@SP
M=D
@Sys.init$L_RETURN.0
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
(Sys.init$L_RETURN.0)
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
(Main.fibonacci)
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
@2
D=A
@SP
A=M-1
D=M-D
@Main.fibonacci$0.TRUE.lt
D;JLT
@SP
A=M-1
M=0
@Main.fibonacci$0.END.lt
0;JMP
(Main.fibonacci$0.TRUE.lt)
@SP
A=M-1
M=-1
(Main.fibonacci$0.END.lt)
@0
D=A
@SP
A=M-1
D=M-D
@Main.fibonacci$1.TRUE.eq
D;JEQ
@SP
A=M-1
M=0
@Main.fibonacci$1.END.eq
0;JMP
(Main.fibonacci$1.TRUE.eq)
@SP
A=M-1
M=-1
(Main.fibonacci$1.END.eq)
@SP
AM=M-1
D=M
@Main.fibonacci$IF_TRUE
D;JEQ
@Main.fibonacci$IF_FALSE
0;JMP
(Main.fibonacci$IF_TRUE)
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
@GLOBAL_COMMON_RETURN
0;JMP
(Main.fibonacci$IF_FALSE)
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
@2
D=A
@SP
A=M-1
M=M-D
@Main.fibonacci$L_RETURN.1
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
(Main.fibonacci$L_RETURN.1)
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
@1
D=A
@SP
A=M-1
M=M-D
@Main.fibonacci$L_RETURN.2
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
(Main.fibonacci$L_RETURN.2)
@SP
AM=M-1
D=M
@SP
A=M-1
M=M+D
@GLOBAL_COMMON_RETURN
0;JMP
(Sys.init)
@4
D=A
@SP
AM=M+1
A=A-1
M=D
@Main.fibonacci$L_RETURN.3
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
(Main.fibonacci$L_RETURN.3)
(Sys.init$WHILE)
@Sys.init$WHILE
0;JMP
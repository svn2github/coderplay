// function SimpleFunction.test 2
(SimpleFunction.test)
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
@LCL
A=M
M=D
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
@LCL
A=M+1
M=D
// push local 0
@LCL
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
// push local 1
@LCL
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
// not
@SP
M=M-1
A=M
D=M
D=!D
@SP
A=M
M=D
@SP
M=M+1
// push argument 0
@ARG
A=M
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
// push argument 1
@ARG
A=M+1
D=M
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
(SimpleFunction.asm.end)
@SimpleFunction.asm.end
0;JMP

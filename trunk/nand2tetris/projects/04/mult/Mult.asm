// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[3], respectively.)

// Put your code here.
// R2 = R0 * R1
    @R2
    M=0     // reset M[R2] to 0
    @R1     // Number of additions
    D=M
    @i      // counter
    M=D     // set the counter to number of additions
(LOOP)
    @i
    D=M     // D = counter
    @END
    D;JEQ   // if counter is 0, end the calculation
    @i
    M=M-1   // decrease the counter by 1 
    @R2
    D=M     // load the previous stored product
    @R0
    D=D+M   // accumulate M[R0] one more time
    @R2
    M=D     // save product back to M[R2]
    @LOOP
    0;JMP   // Goto LOOP for more addition
(END)
    @END
    0;JMP   // infinite loops for ending
    

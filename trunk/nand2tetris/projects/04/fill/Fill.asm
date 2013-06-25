// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// Put your code here.

// We blacken or whiten the screen word by word.
// 16 bit each time we operate. 
// I am not sure how we can turn on/off each individual
// bit instead of each word, or maybe it is rather complicated.

    @i              // The counter of words
    M=0             // reset to zero

(LOOP)
    @KBD    // listen to the keyboard
    D=M

    @WHITE
    D;JEQ // If no key is pressed we white stuff

    // else we black stuff

    @i          
    D=M
    @8192   // Max number of screen word 16*512
    D=D-A   // Check if the counter has reach its maximum value

    @LOOP   // If it is we do nothing, everythin is blacken'd
    D;JGE   

    @i      // Get the correct screen address
    D=M
    @SCREEN
    A=A+D
    M=-1    // Blacken the word
    
    @i
    M=M+1   // increase the counter
    
    @LOOP   // Go back and listen to the keyboard again.
    0;JMP

(WHITE)
    @i
    D=M     // Check if the counter has reach its minimum 0
    
    @LOOP   // if it does we do nothing, everything is whiten'd
    D;JLT

    @i
    D=M
    @SCREEN
    A=A+D
    M=0     // whiten the word

    @i
    M=M-1   // decrease the counter

    @LOOP
    0;JMP

    
    

    

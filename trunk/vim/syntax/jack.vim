" Syntax file for the Jack programming language (nand2tetris)
"
if exists("b:current_syntax")
    finish
endif

syn keyword JackKeywords class constructor method function do let return
syn keyword JackKeywords this var static field true false null
syn keyword JackTypes int boolean char void
syn keyword JackConditions if else while

syn match JackComments "//.*$"

syn region JackString start=+"+ end=+"+
syn region JackMultiComments start="/\*" end="\*/"

hi link JackKeywords     Statement
hi link JackTypes        Type
hi link JackConditions   Conditional
hi link JackComments     Comment
hi link JackMultiComments     Comment
hi link JackString       String

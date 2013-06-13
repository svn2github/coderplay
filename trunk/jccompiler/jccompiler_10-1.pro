; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version of single character in the middle of chapter 10.
;
; :Author:
;   ywang
;
; :Examples:
; ::
;
;
; :History:
;   Created by:    ywang @ Thu 30 May 2013
;   Last modified: ywang @ Wed 05 Jun 2013
;
;-

; --------------------------------------------------------------------- 
; Program Cradle

; --------------------------------------------------------------------- 
; Constant Declarations 
; The tab constant is not needed


; --------------------------------------------------------------------- 
; Variable Declarations
; Lookahead Character is now defined as system variable in the main program

; --------------------------------------------------------------------- 
; Read New Character From Input Stream 

pro GetChar, newInput=newInput
    ; IDL does not have a read function to read a single character from
    ; an input stream and leave the rest of the input untouched. It 
    ; consumes the entire input line and takes the part that it wants 
    ; and discard the rest. So I have to manually simulate the stream
    ; buffer as in the C or other languages.
    if strlen(!jcLineBuffer) gt 0 then begin
        ;printf, -2, 'we have buffer'
        !jcLook = strmid(!jcLineBuffer, 0, 1)
        !jcLineBuffer = strmid(!jcLineBuffer, 1)
    endif else if keyword_set(newInput) then begin
        ;printf, -2, 'we need new input'
        oneLine = ''
        read, oneLine, prompt=''
        !jcLineBuffer = oneLine
        GetChar
    endif else begin
        !jcLook = ''
    endelse
end;

; --------------------------------------------------------------------- 
; Report an Error 

pro Error, s
    print
    print, 'Error: ', s, '.'
end;


; --------------------------------------------------------------------- 
; Report Error and Halt 

pro Abort, s
    Error, s

    ;message, 'Parsing Error'
    retall
end


; --------------------------------------------------------------------- 
; Report What Was Expected

pro Expected, s
    Abort, s + ' Expected'
end

; --------------------------------------------------------------------- 
; Match a Specific Input Character

pro Match, x
    printf, ywglun(setcallhistory=3, uplevel=2), ''
    if !jcLook eq x then GetChar else Expected, '"' + x + '"'
end


; --------------------------------------------------------------------- 
; Recognize an Alpha Character 

function IsAlpha, c
    if strupcase(c) ge 'A' and strupcase(c) le 'Z' $
        then return, 1 $
        else return, 0
end


; --------------------------------------------------------------------- 
; Recognize a Decimal Digit 

function IsDigit, c
    if c ge '0' and c le '9' $
        then return, 1 $
        else return, 0
end

; ---------------------------------------------------------------------
; Recognize an Addop
function IsAddop, c
    void = where(['+','-'] eq c, count)
    return, count
end

; ---------------------------------------------------------------------
; Recognize an Mulop
function IsMulop, c
    void = where(['*','/'] eq c, count)
    return, count
end

; ---------------------------------------------------------------------
; Recognize a Boolean Orop
function IsOrop, c
    void = where(['|','~'] eq c, count)
    return, count
end

; ---------------------------------------------------------------------
; Recognize a Relop Orop
function IsRelop, c
    void = where(['=','#','<','>'] eq c, count)
    return, count
end

; ---------------------------------------------------------------------
; Look for Symbol in Table
function InTable, n
    ST = !jcST
    return, ST[n] ne ' '
end

; --------------------------------------------------------------------- 
; Get an Identifier 

function GetName
    if ~IsAlpha(!jcLook) then Expected, 'Name'
    theName = strupcase(!jcLook);
    GetChar
    return, theName
end


; --------------------------------------------------------------------- 
; Get a Number 

function GetNum
    if ~IsDigit(!jcLook) then Expected, 'Integer'
    Val = 0
    while IsDigit(!jcLook) do begin
        Val = 10*Val + fix(!jcLook)
        GetChar
    endwhile
    return, Val
end


; --------------------------------------------------------------------- 
; Output a String with Tab 

pro Emit, s
    print, string(9B), s, format='(A, A, $)'
end


; --------------------------------------------------------------------- 
; Output a String with Tab and CRLF 

pro EmitLn, s
    printf, ywglun(setcallhistory=3,uplevel=2), ''
    Emit, s
    print
end

; ---------------------------------------------------------------------
; Generate a Unique Label
function NewLabel
    S = string(!jcLcount, format='(I02)')
    !jcLcount += 1
    return, 'L'+S
end

; ---------------------------------------------------------------------
; Post a Label To Output

pro PostLabel, L
    print, L, ':'
end

; ---------------------------------------------------------------------
; Write Header Info
pro Header
    print, 'WARMST'+string(9B)+'EQU $A01E'
end

; ---------------------------------------------------------------------
; Write the Prolog
pro Prolog
    PostLabel, 'Main'
end

; ---------------------------------------------------------------------
; Write the Epilog
pro Epilog
    EmitLn, 'DC WARMST'
    EmitLn, 'END MAIN'
end

; ---------------------------------------------------------------------
; Report an Undefined Identifier
pro Undefined, n
    Abort, 'Undefined Identifier ' + n
end

; ---------------------------------------------------------------------
; Clear the Primary Register
pro Clear
    EmitLn, 'CLR D0'
end

; ---------------------------------------------------------------------
; Negate the Primary Register 
pro Negate
    EmitLn, 'NEG D0'
end;

; ---------------------------------------------------------------------
; Load a Constant Value to Primary Register
pro LoadConst, n
    Emit, 'MOVE #'
    print, strtrim(n,2), ',D0'
end

; ---------------------------------------------------------------------
; Load a Variable to Primary Register
pro LoadVar, Name
    if ~InTable(Name) then Undefined, Name
    EmitLn, 'MOVE ' + Name + '(PC),D0'
end

; ---------------------------------------------------------------------
; Push Primary onto Stack 
pro Push
    EmitLn, 'MOVE D0,-(SP)'
end

; ---------------------------------------------------------------------
; Add Top of Stack to Primary
pro PopAdd
    EmitLn, 'ADD (SP)+,D0'
end;

; ---------------------------------------------------------------------
; Subtract Primary from Top of Stack
pro PopSub
    EmitLn, 'SUB (SP)+,D0'
    Negate
    ;EmitLn, 'NEG D0'
end

; ---------------------------------------------------------------------
; Multiply Top of Stack by Primary
pro PopMul
    EmitLn, 'MULS (SP)+,D0'
end

; ---------------------------------------------------------------------
; Divide Top of Stack by Primary
pro PopDiv;
    EmitLn, 'MOVE (SP)+,D7'
    EmitLn, 'EXT.L D7'
    EmitLn, 'DIVS D0,D7'
    EmitLn, 'MOVE D7,D0'
end

; ---------------------------------------------------------------------
; Store Primary to Variable
pro Store, Name
    if ~InTable(Name) then Undefined, Name
    EmitLn, 'LEA ' + Name + '(PC),A0'
    EmitLn, 'MOVE D0,(A0)'
end

; ---------------------------------------------------------------------
; Complement the Primary Register
pro NotIt
    EmitLn, 'NOT D0'
end

; ---------------------------------------------------------------------
; AND Top of Stack with Primary
pro PopAnd
    EmitLn, 'AND (SP)+,D0'
end

; ---------------------------------------------------------------------
; OR Top of Stack with Primary
pro PopOr
    EmitLn, 'OR (SP)+,D0'
end

; ---------------------------------------------------------------------
; XOR Top of Stack with Primary
pro PopXor
    EmitLn, 'EOR (SP)+,D0'
end

; ---------------------------------------------------------------------
; Compare Top of Stack with Primary
pro PopCompare
    EmitLn, 'CMP (SP)+,D0'
end

; ---------------------------------------------------------------------
; Set D0 If Compare was =
pro SetEqual
    EmitLn, 'SEQ D0'
    EmitLn, 'EXT D0'
end

; ---------------------------------------------------------------------
; Set D0 If Compare was !=
pro SetNEqual
    EmitLn, 'SNE D0'
    EmitLn, 'EXT D0'
end

; ---------------------------------------------------------------------
; Set D0 If Compare was >
pro SetGreater
    EmitLn, 'SLT D0'
    EmitLn, 'EXT D0'
end

; ---------------------------------------------------------------------
; Set D0 If Compare was <
pro SetLess
    EmitLn, 'SGT D0'
    EmitLn, 'EXT D0'
end

; ---------------------------------------------------------------------
; Branch Unconditional
pro Branch, L
    EmitLn, 'BRA ' + L
end

; ---------------------------------------------------------------------
; Branch False
pro BranchFalse, L
    EmitLn, 'TST D0'
    EmitLn, 'BEQ ' + L
end

; ---------------------------------------------------------------------
; Recognize and Translate an IF Construct
pro DoIf
    Match, 'i'
    BoolExpression
    L1 = NewLabel()
    L2 = L1
    BranchFalse, L1
    Block
    if !jcLook eq 'l' then begin
        Match, 'l'
        L2 = NewLabel()
        Branch, 'L2'
        PostLabel, 'L1'
        Block
    endif
    PostLabel, L2
    Match, 'e'
end

; ---------------------------------------------------------------------
; Parse and Translate a WHILE Statement
pro DoWhile
    Match, 'w'
    L1 = NewLabel()
    L2 = NewLabel()
    PostLabel, L1
    BoolExpression;
    BranchFalse, L2
    Block;
    Match, 'e'
    Branch, L1
    PostLabel, L2
end

; ---------------------------------------------------------------------
; Allocate Storage for a Variable
pro Alloc, N
    if InTable(N) then Abort, 'Duplicate Variable Name ' + N
    ST = !jcST
    ST[N] = 'v'
    print, N, ':', string(9B), 'DC ', format='(A,A,A,A,$)'
    if !jcLook eq '=' then begin
        Match, '='
        if !jcLook eq '-' then begin
            print, '-', format='(A,$)'
            Match, '-'
        endif
        print, strtrim(GetNum(),2)
    endif else begin
        print, '0'
    endelse
end

; ---------------------------------------------------------------------
;Process a Data Delcaration
pro Decl
    Match, 'v'
    Alloc, GetName()
    while !jcLook eq ',' do begin
        Match, ','
        Alloc, GetName()
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate Global Declarations
pro TopDecls
    while !jcLook ne 'b' do begin
        case !jcLook of
            'v': Decl
            else: Abort, 'Unrecognized Keyword "' + !jcLook + '"'
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Math Factor
pro Factor
    if !jcLook eq '(' then begin
        Match, '('
        BoolExpression
        Match, ')'
    endif else if IsAlpha(!jcLook) then begin
        LoadVar, GetName()
    endif else begin
        LoadConst, GetNum()
    endelse
end

; ---------------------------------------------------------------------
; Parse and Translate a Negative Factor
pro NegFactor
    Match, '-'
    if IsDigit(!jcLook) then begin
        LoadConst, -GetNum()
    endif else begin
        Factor
        Negate
    endelse
end

; ---------------------------------------------------------------------
; Parse and Translate a Leading Factor
pro FirstFactor
    case !jcLook of
        '+': begin
        Match, '+'
        Factor
    end
    '-': NegFactor
    else: Factor
endcase
end

; ---------------------------------------------------------------------
; Recognize and Translate a Multiply
pro Multiply
    Match, '*'
    Factor
    PopMul
end

; ---------------------------------------------------------------------
; Recognize and Translate a Divide
pro Divide
    Match, '/'
    Factor
    PopDiv
end

; ---------------------------------------------------------------------
; Common Code Used By Term and FirstTerm
pro Term1
    while IsMulop(!jcLook) do begin
        Push
        case !jcLook of
            '*': Multiply
            '/': Divide
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Math Term
pro Term
    Factor
    Term1
end

; ---------------------------------------------------------------------
; Parse and Translate a Leading Term
pro FirstTerm
    FirstFactor
    Term1
end

; ---------------------------------------------------------------------
; Recognize and Translate an Add
pro Add
    Match, '+'
    Term
    PopAdd
end

; ---------------------------------------------------------------------
; Recognize and Translate a Subtract
pro Subtract
    Match, '-'
    Term
    PopSub
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Equals"
pro Equals
    Match, '='
    Expression
    PopCompare
    SetEqual
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Not Equals"
pro NotEquals
    Match, '#'
    Expression
    PopCompare
    SetNEqual
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Less Than"
pro Less
    Match, '<'
    Expression
    PopCompare
    SetLess
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Greater Than"
pro Greater
    Match, '>'
    Expression
    PopCompare
    SetGreater
end

; ---------------------------------------------------------------------
; Parse and Translate a Boolean Factor with Leading NOT
pro NotFactor
    if !jcLook eq '!' then begin
        Match, '!'
        Relation
        NotIt
    endif else begin
        Relation
    endelse
end

; ---------------------------------------------------------------------
; Parse and Translate a Boolean Term
pro BoolTerm
    NotFactor
    while !jcLook eq '&' do begin
        Push
        Match, '&'
        NotFactor
        PopAnd
    endwhile
end

; ---------------------------------------------------------------------
; Recognize and Translate a Boolean OR
pro BoolOr
    Match, '|'
    BoolTerm
    PopOr
end

; ---------------------------------------------------------------------
; Recognize and Translate a Boolean XOR
pro BoolXor
    Match, '~'
    BoolTerm
    PopXor
end

; ---------------------------------------------------------------------
; Parse and Translate a Boolean Expression
pro BoolExpression
    BoolTerm
    while IsOrop(!jcLook) do begin
        Push
        case !jcLook of
            '|': BoolOr
            '~': BoolXor
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Relation
pro Relation
    Expression
    if IsRelop(!jcLook) then begin
        Push
        case !jcLook of
            '=': Equals
            '#': NotEquals
            '<': Less
            '>': Greater
        endcase
    endif
end

; ---------------------------------------------------------------------
; Parse and Translate an Expression
pro Expression
    FirstTerm
    while IsAddop(!jcLook) do begin
        Push
        case !jcLook of
            '+': Add
            '-': Subtract
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate an Assignment Statement
pro Assignment
    Name = GetName()
    Match, '='
    BoolExpression
    Store, Name
end

; ---------------------------------------------------------------------
; Parse and Translate a Block of Statements
pro Block
    while where(['e','l'] eq !jcLook) eq -1 do begin
        case !jcLook of
            'i': DoIf
            'w': DoWhile
            else: Assignment
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Main Program
pro Main
    Match, 'b'
    Prolog
    Block
    Match, 'e'
    Epilog
end

; ---------------------------------------------------------------------
; Parse and Translate a Program
pro Prog
    Match, 'p'
    Header
    TopDecls
    Main
    Match, '.'
end

; --------------------------------------------------------------------- 
; Initialize 

pro Init

    defsysv, '!jcLineBuffer', exists=e
    if e then !jcLineBuffer='' else defsysv, '!jcLineBuffer', ''
    ; Define the global available Lookahead Character
    defsysv, '!jcLook', exists=e
    if e then !jcLook='' else defsysv, '!jcLook', '' 

    defsysv, '!jcLcount', exists=e
    if e then !jcLcount=0 else defsysv, '!jcLcount', 0

    ; Initialize the Symbol Table
    ST = hash()
    for ii=65,90 do begin
        ST[string(byte(ii))] = ' '
    endfor
    defsysv, '!jcST', exists=e
    if e then !jcST=ST else defsysv, '!jcST', ST

    GetChar, /newInput
end


; ---------------------------------------------------------------------
; Main Program 
pro jcCompiler

    Init
    Prog
    if !jcLook ne '' then Abort, 'Unexpected data after "."'

end
; --------------------------------------------------------------------- 


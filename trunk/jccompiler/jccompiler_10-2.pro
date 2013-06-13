; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version with multi-character keywords support in the
; middle of chapter 10. Note although this version does accept multi-
; character variables. It uses only the first letter of the variables
; internally. The next version is going to truely support multi-
; character variable names.
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
;   Last modified: ywang @ Tue 11 Jun 2013
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
    printf, ywglun(setcallhistory=3, uplevel=2), ''
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
    NewLine
    if !jcLook eq x then GetChar else Expected, '"' + x + '"'
    SkipWhite
end

; ---------------------------------------------------------------------
; Match a Specific Input String
pro MatchString, x
    if !jcValue ne x then Expected, '"'+x+'"'
end


; ---------------------------------------------------------------------
; Skip Over a Line
pro NewLine
    while !jcLook eq '' do begin
        GetChar, /newInput
        SkipWhite
    endwhile
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
; Recognize an Alphanumeric Character
function IsAlNum, c
    return, IsAlpha(c) or IsDigit(c)
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
; Recognize White Space 
function IsWhite, c
    void = where([' ',string(9B)] eq c, count) 
    return, count
end

; --------------------------------------------------------------------- 
; Skip Over Leading White Space
pro SkipWhite
    while IsWhite(!jcLook) do begin
        GetChar
    endwhile
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
    return, ST[n] ne ''
end

; ---------------------------------------------------------------------
; Table Lookup
function Lookup, T, s, n
    found = 0
    i = n-1
    while i ge 0 and ~found do begin
        if s eq T[i] then begin
            found = 1
        endif else begin
            i = i-1
        endelse
    endwhile
    return, i
end

; --------------------------------------------------------------------- 
; Get an Identifier 

pro GetName
    NewLine
    if ~IsAlpha(!jcLook) then Expected, 'Name'
    !jcValue = ''
    while IsAlNum(!jcLook) do begin
        !jcValue += strupcase(!jcLook);
        GetChar
    endwhile
    SkipWhite
end


; --------------------------------------------------------------------- 
; Get a Number 

function GetNum
    NewLine
    if ~IsDigit(!jcLook) then Expected, 'Integer'
    Val = 0
    while IsDigit(!jcLook) do begin
        Val = 10*Val + fix(!jcLook)
        GetChar
    endwhile
    SkipWhite
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
    BoolExpression
    L1 = NewLabel()
    L2 = L1
    BranchFalse, L1
    Block
    if !jcToken eq 'l' then begin
        L2 = NewLabel()
        Branch, 'L2'
        PostLabel, 'L1'
        Block
    endif
    PostLabel, L2
    MatchString, 'ENDIF'
end

; ---------------------------------------------------------------------
; Parse and Translate a WHILE Statement
pro DoWhile
    L1 = NewLabel()
    L2 = NewLabel()
    PostLabel, L1
    BoolExpression;
    BranchFalse, L2
    Block;
    MatchString, 'ENDWHILE'
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
    GetName
    Alloc, strmid(!jcValue, 0, 1)
    while !jcLook eq ',' do begin
        Match, ','
        GetName
        Alloc, strmid(!jcValue, 0, 1)
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate Global Declarations
pro TopDecls
    Scan
    while !jcToken ne 'b' do begin
        case !jcToken of
            'v': Decl
            else: Abort, 'Unrecognized Keyword "' + !jcValue + '"'
        endcase
        Scan
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
        GetName
        LoadVar, strmid(!jcValue, 0, 1)
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
    Name = strmid(!jcValue, 0, 1)
    Match, '='
    BoolExpression
    Store, Name
end

; ---------------------------------------------------------------------
; Parse and Translate a Block of Statements
pro Block
    Scan
    while where(['e','l'] eq !jcToken) eq -1 do begin
        case !jcToken of
            'i': DoIf
            'w': DoWhile
            else: Assignment
        endcase
        Scan
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Main Program
pro Main
    MatchString, 'BEGIN'
    Prolog
    Block
    MatchString, 'END'
    Epilog
end

; ---------------------------------------------------------------------
; Parse and Translate a Program
pro Prog
    Scan
    MatchString, 'PROGRAM'
    Header
    TopDecls
    Main
    Match, '.'
end

; ---------------------------------------------------------------------
; Get an Identifier and Scan it for Keywords
pro Scan
    GetName
    !jcToken = strmid(!jcKWcode, Lookup(!jcKWlist, !jcValue, !jcNKW)+1, 1)
    ;print, 'token: ', !jcToken, '   value: ', !jcValue
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

    defsysv, '!jcToken', exists=e
    if e then !jcToken='' else defsysv, '!jcToken', ''
    defsysv, '!jcValue', exists=e
    if e then !jcValue='' else defsysv, '!jcValue', ''

    ; Initialize the Symbol Table
    ST = hash()
    for ii=65,90 do begin
        ST[string(byte(ii))] = ''
    endfor
    defsysv, '!jcST', exists=e
    if e then !jcST=ST else defsysv, '!jcST', ST

    defsysv, '!jcNKW', exists=e
    if e then !jcNKW = 9 else defsysv, '!jcNKW', 9

    defsysv, '!jcNKW1', exists=e
    if e then !jcNKW1 = 10 else defsysv, '!jcNKW1', 10

    KWlist = ['IF','ELSE','ENDIF','WHILE','ENDWHILE','VAR','BEGIN','END','PROGRAM']
    defsysv, '!jcKWlist', exists=e
    if e then !jcKWlist=KWlist else defsysv, '!jcKWlist', KWlist

    KWcode = 'xilewevbep'
    defsysv, '!jcKWcode', exists=e
    if e then !jcKWcode=KWcode else defsysv, '!jcKWcode', KWcode

    SkipWhite
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


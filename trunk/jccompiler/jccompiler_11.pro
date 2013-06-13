; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version at the end of Chapter 11 that features a dedicate
; Token generate routine.
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
;   Last modified: ywang @ Wed 12 Jun 2013
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
; Match a Specific Input String
pro MatchString, x
    if !jcValue ne x then Expected, '"'+x+'"'
    if !jcValue eq 'END' then return
    Next
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
    void = where([' ',string(9B),''] eq c, count) 
    return, count
end

; --------------------------------------------------------------------- 
; Skip Over Leading White Space
pro SkipWhite
    while IsWhite(!jcLook) do begin
        ; Get new input if the lookahead char is an empty string
        if !jcLook eq '' then newInput=1 else newInput=0
        GetChar, newInput=newInput
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
; Locate a Symbol in Table
function Locate, N
    return, Lookup(!jcST, N, !jcNEntry)
end

; ---------------------------------------------------------------------
; Look for Symbol in Table
function InTable, n
    ST = !jcST
    return, Lookup(ST, n, !jcMaxEntry) ne -1
end

; ---------------------------------------------------------------------
; Check to See if an Identifier is in the Symbol Table
pro CheckTable, N
    if ~InTable(N) then Undefined, N
end

; ---------------------------------------------------------------------
; Check the Symbol Table for a Duplicate Identifier
pro CheckDup, N
    if InTable(N) then Duplicate, N
end

; --------------------------------------------------------------------- 
; Get an Identifier 

pro GetName
    SkipWhite
    if ~IsAlpha(!jcLook) then Expected, 'Identifier'
    !jcToken = 'x'
    !jcValue = ''
    repeat begin
        !jcValue += strupcase(!jcLook);
        GetChar
    endrep until ~IsAlNum(!jcLook)
end


; --------------------------------------------------------------------- 
; Get a Number 

pro GetNum
    SkipWhite
    if ~IsDigit(!jcLook) then Expected, 'Integer'
    !jcToken = '#'
    !jcValue = ''
    Val = 0
    repeat begin
        !jcValue += !jcLook
        GetChar
    endrep until ~IsDigit(!jcLook)
end

; ---------------------------------------------------------------------
; Get an Operator
pro GetOp
    SkipWhite
    !jcToken = !jcLook
    !jcValue = !jcLook
    GetChar
end

; ---------------------------------------------------------------------
; Get the next Input Token
pro Next
    SkipWhite
    if IsAlpha(!jcLook) then begin
        GetName
    endif else if IsDigit(!jcLook) then begin
        GetNum
    endif else begin
        GetOp
    endelse
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
    ;EmitLn, 'LIB TINYLIB'
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
; Report a Duplicate Identifier
pro Duplicate, n
    Abort, 'Duplicate Identifier ' + n
end

; ---------------------------------------------------------------------
; Check to Make Sure the Current Token is an Identifier
pro CheckIdent
    if !jcToken ne 'x' then Expected, 'Identifier'
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
; Set D0 If Compare was <=
pro SetLessOrEqual
    EmitLn, 'SGE D0'
    EmitLn, 'EXT D0'
end

; ---------------------------------------------------------------------
; Set D0 If Compare was >=
pro SetGreaterOrEqual
    EmitLn, 'SLE D0'
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
; Read Variable to Primary Register
pro ReadIt
    EmitLn, 'BSR READ'
    Store, !jcValue
end

; ---------------------------------------------------------------------
; Write Variable from Primary Register
pro WriteIt
    EmitLn, 'BSR WRITE'
end

; ---------------------------------------------------------------------
; Read a Single Variable
pro ReadVar
    CheckIdent
    CheckTable, !jcValue
    ReadIt, !jcValue
    Next
end

; ---------------------------------------------------------------------
; Process a Read Statement
pro DoRead
    Next
    MatchString, '('
    ReadVar
    while !jcToken eq ',' do begin
        Next
        ReadVar
    endwhile
    MatchString, ')'
end

; ---------------------------------------------------------------------
; Process a Write Statement
pro DoWrite
    Next
    MatchString, '('
    Expression
    WriteIt
    while !jcLook eq ',' do begin
        Next
        Expression
        WriteIt
    endwhile
    MatchString, ')'
end

; ---------------------------------------------------------------------
; Recognize and Translate an IF Construct
pro DoIf
    Next
    BoolExpression
    L1 = NewLabel()
    L2 = L1
    BranchFalse, L1
    Block
    if !jcToken eq 'l' then begin
        Next
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
    Next
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
; Add a New Entry to Symbol Table
pro AddEntry, N, T
    CheckDup, N
    if !jcNEntry eq !jcMaxEntry then Abort, 'Symbol Table Full'

    ST = !jcST 
    ST[!jcNEntry] = N

    STtype = !jcSTtype
    STtype[!jcNEntry] = T

    !jcNEntry += 1
end

; ---------------------------------------------------------------------
; Allocate Storage for a Variable
pro Allocate, Name, Val
    print, Name, ':', string(9B), 'DC ' + Val
end

; ---------------------------------------------------------------------
; Allocate Storage for a Variable
pro Alloc
    Next
    if !jcToken ne 'x' then Expected, 'Variable Name'
    CheckDup, !jcValue
    AddEntry, !jcValue, 'v'
    Allocate, !jcValue, '0'
    Next
end

; ---------------------------------------------------------------------
; Parse and Translate Global Declarations
pro TopDecls
    Scan
    while !jcToken eq 'v' do begin
        Alloc
        while !jcToken eq ',' do begin
            Alloc
        endwhile
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Math Factor
pro Factor
    if !jcToken eq '(' then begin
        Next
        BoolExpression
        MatchString, ')'
    endif else begin
        if !jcToken eq 'x' then begin
            LoadVar, !jcValue
        endif else if !jcToken eq '#' then begin
            LoadConst, !jcValue
        endif else begin
            Expected, 'Math Factor'
        endelse
        Next
    endelse
end

; ---------------------------------------------------------------------
; Recognize and Translate a Multiply
pro Multiply
    Next
    Factor
    PopMul
end

; ---------------------------------------------------------------------
; Recognize and Translate a Divide
pro Divide
    Next
    Factor
    PopDiv
end

; ---------------------------------------------------------------------
; Parse and Translate a Math Term
pro Term
    Factor
    while IsMulop(!jcToken) do begin
        Push
        case !jcToken of
            '*': Multiply
            '/': Divide
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Recognize and Translate an Add
pro Add
    Next
    Term
    PopAdd
end

; ---------------------------------------------------------------------
; Recognize and Translate a Subtract
pro Subtract
    Next
    Term
    PopSub
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Equals"
pro Equal
    NextExpression
    SetEqual
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Not Equals"
pro NotEqual
    NextExpression
    SetNEqual
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Less Than"
pro Less
    Next
    case !jcToken of
        '=': LessOrEqual
        '>': NotEqual
        else: begin
            CompareExpression
            SetLess
        end
    endcase
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Less Than or Equal"
pro LessOrEqual
    NextExpression
    SetLessOrEqual
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Greater Than"
pro Greater
    Next
    if !jcToken eq '=' then begin
        NextExpression
        SetGreaterOrEqual
    endif else begin
        CompareExpression
        SetGreater
    endelse
end

; ---------------------------------------------------------------------
; Parse and Translate a Boolean Factor with Leading NOT
pro NotFactor
    if !jcToken eq '!' then begin
        Next
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
    while !jcToken eq '&' do begin
        Push
        Next
        NotFactor
        PopAnd
    endwhile
end

; ---------------------------------------------------------------------
; Recognize and Translate a Boolean OR
pro BoolOr
    Next
    BoolTerm
    PopOr
end

; ---------------------------------------------------------------------
; Recognize and Translate a Boolean XOR
pro BoolXor
    Next
    BoolTerm
    PopXor
end

; ---------------------------------------------------------------------
; Parse and Translate a Boolean Expression
pro BoolExpression
    BoolTerm
    while IsOrop(!jcToken) do begin
        Push
        case !jcToken of
            '|': BoolOr
            '~': BoolXor
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Relation
pro Relation
    Expression
    if IsRelop(!jcToken) then begin
        Push
        case !jcToken of
            '=': Equal
            '<': Less
            '>': Greater
        endcase
    endif
end

; ---------------------------------------------------------------------
; Parse and Translate an Expression
pro Expression
    if IsAddop(!jcToken) Then begin
        Clear
    endif else begin
        Term
    endelse
    while IsAddop(!jcToken) do begin
        Push
        case !jcLook of
            '+': Add
            '-': Subtract
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Get Another Expression and Compare
pro CompareExpression
    Expression
    PopCompare
end

; ---------------------------------------------------------------------
; Get the Next Expression and Compare
pro NextExpression
    Next
    CompareExpression
end

; ---------------------------------------------------------------------
; Parse and Translate an Assignment Statement
pro Assignment
    CheckTable, !jcValue
    Name = !jcValue
    Next
    MatchString, '='
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
            'R': DoRead
            'W': DoWrite
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
; Scan the Current Identifier for Keywords
pro Scan
    if !jcToken eq 'x' then begin
        !jcToken = strmid(!jcKWcode, Lookup(!jcKWlist, !jcValue, !jcNKW)+1, 1)
    endif
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


    defsysv, '!jcMaxEntry', exists=e
    if e then !jcMaxEntry=100 else defsysv, '!jcMaxEntry', 100
    defsysv, '!jcNEntry', exists=e
    if e then !jcNEntry=0 else defsysv, '!jcNEntry', 0

    ; Initialize the Symbol Table
    ST = hash() & STtype = hash()
    for ii=0,!jcMaxEntry do begin
        ST[ii] = ''
        STtype[ii] = ''
    endfor
    defsysv, '!jcST', exists=e
    if e then !jcST=ST else defsysv, '!jcST', ST
    defsysv, '!jcSTtype', exists=e
    if e then !jcSTtype=STtype else defsysv, '!jcSTtype', STtype

    defsysv, '!jcNKW', exists=e
    if e then !jcNKW = 9 else defsysv, '!jcNKW', 9

    defsysv, '!jcNKW1', exists=e
    if e then !jcNKW1 = 10 else defsysv, '!jcNKW1', 10

    KWlist = ['IF','ELSE','ENDIF','WHILE','ENDWHILE', $
        'READ', 'WRITE', 'VAR','END']
    defsysv, '!jcKWlist', exists=e
    if e then !jcKWlist=KWlist else defsysv, '!jcKWlist', KWlist

    KWcode = 'xileweRWve'
    defsysv, '!jcKWcode', exists=e
    if e then !jcKWcode=KWcode else defsysv, '!jcKWcode', KWcode

    SkipWhite
    Next
end


; ---------------------------------------------------------------------
; Main Program 
pro jcCompiler

    Init
    MatchString, 'PROGRAM'
    Header
    TopDecls
    MatchString, 'BEGIN'
    Prolog
    Block
    MatchString, 'END'
    Epilog

end
; --------------------------------------------------------------------- 


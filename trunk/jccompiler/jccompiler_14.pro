; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version at the end of chapter 14 with simple data type
; and coersion.
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
;   Last modified: ywang @ Thu 13 Jun 2013
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
        !jcLook = strmid(!jcLineBuffer, 0, 1)
        !jcLineBuffer = strmid(!jcLineBuffer, 1)
    endif else if keyword_set(newInput) then begin
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
; Dump the Symbol Table
pro DumpTable
    ST = !jcST
    for ii=65,90 do begin
        idx = string(byte(ii))
        if ST[idx] ne '?' then print, idx, ' ', ST[idx]
    endfor
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
; Recognize a Mulop
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
; Recognize a Relop
function IsRelop, c
    void = where(['=','#','<','>'] eq c, count)
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
; Skip Over an End-of-Line
pro Fin
    if !jcLook eq '' then GetChar, /newInput
end

; ---------------------------------------------------------------------
; Report Type of a Variable
function TypeOf, N
    ST = !jcST
    return, ST[N]
end

; ---------------------------------------------------------------------
; Report if a Variable is in the Table
function InTable, N
    return, TypeOf(N) ne '?'
end

; ---------------------------------------------------------------------
; Check for a Duplicate Variable Name
pro CheckDup, N
    if InTable(N) then Abort, 'Duplicate Name ' + N
end

; ---------------------------------------------------------------------
; Add Entry to Table
pro AddEntry, N, T
    CheckDup, N
    ST = !jcST
    ST[N] = T
end

; --------------------------------------------------------------------- 
; Match a Specific Input Character
pro Match, x
    printf, ywglun(setcallhistory=3, uplevel=2), ''
    if !jcLook eq x then GetChar else Expected, '"' + x + '"'
end

; --------------------------------------------------------------------- 
; Get an Identifier 

function GetName
    if ~IsAlpha(!jcLook) then Expected, 'Name'
    theName = strupcase(!jcLook);
    GetChar
    SkipWhite
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
    theNum = Val
    SkipWhite
    return, theNum
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
; Generate a Move Instruction
pro Move, Size1, Source, Dest
    EmitLn, 'MOVE.' + Size1 + ' ' + Source + ',' + Dest
end

; --------------------------------------------------------------------- 
; Initialize 
pro Init
    ; Define the global available Lookahead Character
    setsysv, '!jcLineBuffer', ''
    setsysv, '!jcLook', ''

    ; The Symbol Table
    ST = hash()
    for ii=65,90 do ST[string(byte(ii))] = '?'
    setsysv, '!jcST', ST

    GetChar, /newInput
end

; ---------------------------------------------------------------------
; Load a Constant to the Primary Register
pro LoadConst, N, Typ
    Move, Typ, '#'+strtrim(N,2), 'D0'
end

; ---------------------------------------------------------------------
; Load a Constant to the Primary Register
function LoadNum, N
    if abs(N) le 127 then begin
        Typ = 'B'
    endif else if abs(N) le 32767 then begin
        Typ = 'W'
    endif else begin
        Typ = 'L'
    endelse
    LoadConst, N, Typ
    return, Typ
end

; ---------------------------------------------------------------------
; Recognize a Legal Variable Type
function IsVarType, c
    void = where(['B', 'W', 'L'] eq c, count)
    return, count
end

; ---------------------------------------------------------------------
; Get a Variable Type from the Symbol Table
function VarType, Name
    Typ = TypeOf(Name)
    if ~IsVarType(Typ) then Abort, 'Identifier ' + Name + ' is not a variable'
    return, Typ
end

; ---------------------------------------------------------------------
; Load a Variable to the Primary Register
function Load, Name
    Typ = VarType(Name)
    LoadVar, Name, Typ
    return, Typ
end

; ---------------------------------------------------------------------
; Generate Code for Allocation of a Variable
pro AllocVar, N, T
    print, N, ':', string(9B), 'DC.', T, ' 0'
end

; ---------------------------------------------------------------------
; Allocate Storage for a Variable
pro Alloc, N, T
    AddEntry, N, T
    AllocVar, N, T
end

; ---------------------------------------------------------------------
; Load a Variable to Primary Register
pro LoadVar, Name, Typ
    Move, Typ, Name + '(PC)', 'D0'
end

; ---------------------------------------------------------------------
; Store Primary Register to Variable
pro StoreVar, Name, Typ
    EmitLn, 'LEA ' + Name + '(PC),A0'
    Move, Typ, 'D0', '(A0)'
end

; ---------------------------------------------------------------------
; Store a Variable from the Primary Register
pro Store, Name, T1
    T2 = VarType(Name)
    Convert, T1, T2
    StoreVar, Name, T2
end

; ---------------------------------------------------------------------
; Convert a Data Item from One Type to Another
pro Convert, Source, Dest, Reg
    if Source ne Dest then begin
        if Source eq 'B' then EmitLn, 'AND.W #$FF,'+Reg
        if Dest eq 'L' then EmitLn, 'EXT.L '+Reg
    endif
end

; ---------------------------------------------------------------------
; Promote the Size of a Register Value
function Promote, T1, T2, Reg
    Typ = T1
    if T1 ne T2 then begin
        if T1 eq 'B' or (T1 eq 'W' and T2 eq 'L') then begin
            Convert, T1, T2, Reg
            Typ = T2
        endif
    endif
    return, Typ
end

; ---------------------------------------------------------------------
; Force both Arguments to Same Type
function SameType, T1, T2
    T1 = Promote(T1, T2, 'D7')
    return, Promote(T2, T1, 'D0')
end

; ---------------------------------------------------------------------
; Process a Term with Leading Unary Operator
function Unop
    Clear
    return, 'W'
end

; ---------------------------------------------------------------------
; Push Primary onto Stack
pro Push, Size1
    Move, Size1, 'D0', '-(SP)'
end

; ---------------------------------------------------------------------
; Pop Stack into Secondary Register
pro Pop, Size1
    Move, Size1, '(SP)+', 'D7'
end

; ---------------------------------------------------------------------
; Generate Code to Add Primary to the Stack
function PopAdd, T1, T2
    Pop, T1
    T2 = SameType(T1, T2)
    GenAdd, T2
    return, T2
end

; ---------------------------------------------------------------------
; Generate Code to Subtract Primary from the stack
function PopSub, T1, T2
    Pop, T1
    T2 = SameType(T1, T2)
    GenSub, T2
    return, T2
end

; ---------------------------------------------------------------------
; Add Top of Stack to Primary
pro GenAdd, Size1
    EmitLn, 'ADD.' + Size1 + ' D7,D0'
end

; ---------------------------------------------------------------------
; Subtract Primary from Top of Stack
pro GenSub, Size1
    EmitLn, 'SUB.' + Size1 + ' D7,D0'
    EmitLn, 'NEG.' + Size1 + ' D0'
end

; ---------------------------------------------------------------------
; Generate Code to Multiply Primary by Stack
function PopMul, T1, T2
    Pop, T1
    T = SameType(T1, T2)
    Convert, T, 'W', 'D7'
    Convert, T, 'W', 'D0'
    if T eq 'L' then begin
        GenLongMult
    endif else begin
        GenMult
    endelse
    if T eq 'B' then begin
        return, 'W'
    endif else begin
        return, 'L'
    endelse
end

; ---------------------------------------------------------------------
; Generate Code to Divide Stack by the Primary
function PopDiv, T1, T2
    Pop, T1
    Convert, T1, 'L', 'D7'
    if T1 eq 'L' or T2 eq 'L' then begin
        Convert, T2, 'L', 'D0'
        GenLongDiv
        return, 'L'
    endif else begin
        Convert, T2, 'W', 'D0'
        GenDiv
        return, 'T1'
    endelse
end

; ---------------------------------------------------------------------
; Multiply Top of Stack by Primary (Word)
pro GenMult
    EmitLn, 'MULS D7,D0'
end

; ---------------------------------------------------------------------
; Multiply Top of Stack by Primary (Long)
pro GenLongMult
    EmitLn, 'JSR MUL32'
end

; ---------------------------------------------------------------------
; Divide Top of Stack by Primary
pro GenDiv
    EmitLn, 'DIVS D0,D7'
    Move, 'W', 'D7', 'D0'
end

; ---------------------------------------------------------------------
; Divide Top of Stack by Primary
pro GenLongDiv
    EmitLn, 'JSR DIV32'
end

; ---------------------------------------------------------------------
; Recognize and Translate an Add
function Add, T1
    Match, '+'
    return, PopAdd(T1, Term())
end

; ---------------------------------------------------------------------
; Recognize and Translate a Subtract
function Subtract, T1
    Match, '-'
    return, PopSub(T1, Term())
end

; ---------------------------------------------------------------------
; Recognize and Translate a Multiply
function Multiply, T1
    Match, '*'
    return, PopMul(T1, Factor())
end

; ---------------------------------------------------------------------
; Recognize and Translate a Divide
function Divide, T1
    Match, '/'
    return, PopDiv(T1, Factor())
end

; ---------------------------------------------------------------------
; Parse and Translate a Factor
function Factor
    if !jcLook eq '(' then begin
        Match, '('
        Fac = Expression()
        Match, ')'
    endif else if IsAlpha(!jcLook) then begin
        fac = Load(GetName())
    endif else begin
        fac = LoadNum(GetNum())
    endelse
end

; ---------------------------------------------------------------------
; Parse and Translate a Term
function Term
    Typ = Factor()
    while IsMulop(!jcLook) do begin
        Push, Typ
        case !jcLook of
            '*': Typ = Multiply(Typ)
            '/': Typ = Divide(Typ)
        endcase
    endwhile
    return, Typ
end

; ---------------------------------------------------------------------
; Parse and Translate an Expression
function Expression
    if IsAddop(!jcLook) then begin
        Typ = Unop()
    endif else begin
        Typ = Term()
    endelse
    while IsAddop(!jcLook) do begin
        Push, Typ
        case !jcLook of
            '+': Typ = Add(Typ)
            '-': Typ = Subtract(Typ)
        endcase
    endwhile
    return, Typ
end

; ---------------------------------------------------------------------
; Parse and Translate an Assignment Statement
pro Assignment
    Name = GetName()
    Match, '='
    Store, Name, Expression()
end

; ---------------------------------------------------------------------
; Parse and Translate a Block of Statements
pro Block
    while !jcLook ne '.' do begin
        Assignment
        Fin
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Data Declaration
pro Decl
    Typ = GetName()
    Alloc, GetName(), Typ
end

; ---------------------------------------------------------------------
; Parse and Translate Global Declarations
pro TopDecls
    while !jcLook ne 'B' do begin
        switch !jcLook of 
            'b':
            'w':
            'l': begin
                Decl
                break
            end
            else: Abort, 'Unrecognized Keyword ' + !jcLook
        endswitch
        Fin
    endwhile
end


; ---------------------------------------------------------------------
; Main Program 
pro jcCompiler

    Init
    TopDecls
    Match, 'B'
    Fin
    Block
    DumpTable
    
end
; --------------------------------------------------------------------- 


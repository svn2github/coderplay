; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version in Chapter 13 with call by reference procedures.
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

    retall
end


; --------------------------------------------------------------------- 
; Report What Was Expected

pro Expected, s
    printf, ywglun(setcallhistory=3, uplevel=2), ''
    Abort, s + ' Expected'
end

; ---------------------------------------------------------------------
; Report an Undefined Identifier
pro Undefined, n
    Abort, 'Undefined Identifier ' + n
end

; ---------------------------------------------------------------------
; Report an Duplicate Identifier
pro Duplicate, n
    Abort, 'Duplicate Identifier ' + n
end

; ---------------------------------------------------------------------
; Get Type of Symbol
function TypeOf, n
    ST = !jcST
    if IsParam(n) then begin
        return, 'f'
    endif else begin
        return, ST[n]
    endelse
end

; ---------------------------------------------------------------------
; Look for Symbol in Table
function InTable, n
    ST = !jcST
    return, ST[n] ne ' '
end

; ---------------------------------------------------------------------
; Add a New Symbol to Table
pro AddEntry, Name, T
    if InTable(Name) then Duplicate, Name
    ST = !jcST
    ST[Name] = T
end

; ---------------------------------------------------------------------
; Check and Entry to Make Sure It's a Variable
pro CheckVar, Name
    if ~InTable(Name) then Undefined, Name
    if TypeOf(Name) ne 'v' then Abort, Name + ' is not a variable'
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
    return, theName
end


; --------------------------------------------------------------------- 
; Get a Number 

function GetNum
    if ~IsDigit(!jcLook) then Expected, 'Integer'
    theNum = !jcLook
    GetChar
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
; Post a Label To Output
pro PostLabel, L
    print, L, ':'
end

; ---------------------------------------------------------------------
; Load a Variable to the Primary Register
pro LoadVar, Name
    CheckVar, Name
    EmitLn, 'MOVE ' + Name + '(PC),D0'
end

; ---------------------------------------------------------------------
; Store the Primary Register
pro StoreVar, Name
    CheckVar, Name
    EmitLn, 'LEA ' + Name + '(PC),A0'
    EmitLn, 'MOVE D0,(A0)'
end

; ---------------------------------------------------------------------
; Generate a Procedure Call Instruction
pro Call, Name
    EmitLn, 'BSR ' + Name
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
; Write the Prolog for a Procedure
pro ProcProlog, N
    PostLabel, N
    EmitLn, 'LINK A6,#0'
end

; ---------------------------------------------------------------------
; Write the Epilog for a Procedure
pro ProcEpilog
    EmitLn, 'UNLK A6'
    EmitLn, 'RTS'
end

; ---------------------------------------------------------------------
; Push Primary onto Stack
pro Push
    EmitLn, 'MOVE D0,-(SP)'
end

; ---------------------------------------------------------------------
; Initialize Parameter Table to Null
pro ClearParams
    Params = !jcParams
    for ii=65,90 do Params[string(byte(ii))] = 0
    !jcNumParams = 0
end

; --------------------------------------------------------------------- 
; Initialize 
pro Init
    ; Define the global available Lookahead Character
    setsysv, '!jcLineBuffer', ''
    setsysv, '!jcLook', ''

    ; The Symbol Table
    ST = hash()
    for ii=65,90 do ST[string(byte(ii))] = ' '
    setsysv, '!jcST', ST

    ; The formal Parameter symbol table
    setsysv, '!jcParams', hash()
    setsysv, '!jcNumParams', 0
    ClearParams

    GetChar, /newInput
end

; ---------------------------------------------------------------------
; Parse and Translate an Expression
; Vestigial Version
pro Expression
    Name = GetName()
    if IsParam(Name) then begin
        LoadParam, ParamNumber(Name)
    endif else begin
        LoadVar, Name
    endelse
end

; ---------------------------------------------------------------------
; Process an Actual Parameter
pro Param
    EmitLn, 'PEA ' + GetName() + '(PC)'
end

; ---------------------------------------------------------------------
; Process the Parameter List for a Procedure Call
function ParamList
    N = 0
    Match, '('
    if !jcLook ne ')' then begin
        Param
        N += 1
        while !jcLook eq ',' do begin
            Match, ','
            Param
            N += 1
        endwhile
    endif
    Match, ')'
    return, 4 * N
end

; ---------------------------------------------------------------------
; Adjust the Stack Pointer Upwards by N Bytes
pro CleanStack, N
    if N gt 0 then begin
        Emit, 'ADD #'
        print, strtrim(N,2), ',SP'
    endif
end

; ---------------------------------------------------------------------
; Call a Procedure
pro CallProc, Name
    N = ParamList()
    Call, Name
    CleanStack, N
end

; ---------------------------------------------------------------------
; Parse and Translate an Assignment Statement
pro Assignment, Name
    Match, '='
    Expression
    if IsParam(Name) then begin
        StoreParam, ParamNumber(Name)
    endif else begin
        StoreVar, Name
    endelse
end

; ---------------------------------------------------------------------
; Decide if a Statement is an Assignment or Procedure Call
pro AssignOrProc
    Name = GetName()
    case TypeOf(Name) of
        ' ': Undefined, Name
        'v': Assignment, Name
        'f': Assignment, Name
        'p': CallProc, Name
        else: Abort, 'Identifier ' + Name + ' Cannot Be Used Here'
    endcase
end

; ---------------------------------------------------------------------
; Parse and Translate a Block of Statements
pro DoBlock
    while where(['e'] eq !jcLook) eq -1 do begin
        AssignOrProc
        Fin
    endwhile
end

; ---------------------------------------------------------------------
; Process a Formal Parameter
pro FormalParam
    AddParam, GetName()
end

; ---------------------------------------------------------------------
; Process the Formal Parameter List of a Procedure
pro FormalList
    Match, '('
    if !jcLook ne ')' then begin
        FormalParam
        while !jcLook eq ',' do begin
            Match, ','
            FormalParam
        endwhile
    endif
    Match, ')'
end

; ---------------------------------------------------------------------
; Find the Parameter Number
function ParamNumber, N
    Params = !jcParams
    return, Params[N]
end

; ---------------------------------------------------------------------
; See if an Identifier is a Parameter
function IsParam, N
    Params = !jcParams
    return, Params[N] ne 0
end

; ---------------------------------------------------------------------
; Add a New Parameter to Table
pro AddParam, Name
    if IsParam(Name) then Duplicate, Name
    !jcNumParams += 1
    Params = !jcParams
    Params[Name] = !jcNumParams
end

; ---------------------------------------------------------------------
; Load a Parameter to the Primary Register
pro LoadParam, N
    Offset = 8 + 4 * (!jcNumParams - N)
    Emit, 'MOVE.L '
    print, strtrim(Offset,2), '(A6),A0'
    EmitLn, 'MOVE (A0),D0'
end

; ---------------------------------------------------------------------
; Store a Parameter from the Primary Register
pro StoreParam, N
    Offset = 8 + 4 * (!jcNumParams - N)
    Emit, 'MOVE.L '
    print, strtrim(Offset,2), '(A6),A0'
    EmitLn, 'MOVE D0,(A0)'
end

; ---------------------------------------------------------------------
; Parse and Translate a Procedure Declaration
pro DoProc
    Match, 'p'
    N = GetName()
    FormalList
    Fin
    if InTable(N) then Duplicate, N
    ST = !jcST
    ST[N] = 'p'
    ProcProlog, N
    BeginBlock
    ProcEpilog
    ClearParams
end

; ---------------------------------------------------------------------
; Parse and Translate a Main Program
pro DoMain
    Match, 'P'
    N = GetName()
    Fin
    if InTable(N) then Duplicate, N
    Prolog
    BeginBlock
end

; ---------------------------------------------------------------------
; Parse and Translate a Begin-Block
pro BeginBlock
    Match, 'b'
    Fin
    DoBlock
    Match, 'e'
    Fin
end

; ---------------------------------------------------------------------
; Allocate Storage for a Variable
pro Alloc, N
    if InTable(N) then Duplicate, N
    ST = !jcST
    ST[N] = 'v'
    print, N, ':', string(9B), 'DC 0'
end

; ---------------------------------------------------------------------
; Parse and Translate a Date Declaration
pro Decl
    Match, 'v'
    Alloc, GetName()
end

; ---------------------------------------------------------------------
; Parse and Translate Global Declarations
pro TopDecls
    while !jcLook ne 'b' do begin
        case !jcLook of
            'v': Decl
            'p': DoProc
            'P': DoMain
            else: Abort, 'Unrecognized Keyword ' + !jcLook
        endcase
        Fin
    endwhile
end

; ---------------------------------------------------------------------
; Main Program 
pro jcCompiler

    Init
    TopDecls
    Epilog
    
end
; --------------------------------------------------------------------- 


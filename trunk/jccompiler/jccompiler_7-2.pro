; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version at the end of Chapter 7. It features a multiple
; character scanner, an If control struct. Also note GetName is doing
; a lot stuff, including getting name for both variable and function
; and also request for next line input when linebuffer is out.
; 
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
;   Last modified: ywang @ Tue 04 Jun 2013
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
    ;printf, ywglun(setcallhistory=3, uplevel=2), ''
    Abort, s + ' Expected'
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
; Match a Specific Input Character

pro Match, x
    if !jcLook eq x then GetChar else Expected, '"' + x + '"'
end


; ---------------------------------------------------------------------
; Table Lookup
; If the input string matches a table entry, return the entry index.
; If not, return a Zero.
function Lookup, table, s, n
    found = 0
    i = n
    while i gt 0 and ~found do begin
        if s eq table[i] then begin
            found = 1
        endif else begin
            i -= 1
        endelse
    endwhile
    return, i
end


; --------------------------------------------------------------------- 
; Get an Identifier 
pro GetName
    if !jcLook eq '' and !jcLineBuffer eq '' then GetChar, /newInput
    if ~IsAlpha(!jcLook) then Expected, 'Name'
    value = ''
    while IsAlNum(!jcLook) do begin
        value += strupcase(!jcLook);
        GetChar
    endwhile
    SkipWhite
    !jcValue = value
end


; --------------------------------------------------------------------- 
; Get a Number 
pro GetNum
    if ~IsDigit(!jcLook) then Expected, 'Integer'
    value = ''
    while IsDigit(!jcLook) do begin
        value += !jcLook
        GetChar
    endwhile
    SkipWhite
    !jcToken = '#'
    !jcValue = value
end

; ---------------------------------------------------------------------
; Get an Identifier and Scan it for Keywords
pro Scan
    GetName
    !jcToken = strmid(!jcKWcode, Lookup(!jcKWlist, !jcValue, 4), 1)
end

; ---------------------------------------------------------------------
; Match a Specific Input String
pro MatchString, x
    if !jcValue ne x then Expected, '"' + x + '"'
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
; Parse and Translate an Identifier
pro Ident
    GetName
    if !jcLook eq '(' then begin
        Match, '('
        Match, ')'
        EmitLn, 'BSR ' + !jcValue ; function call
    endif else begin
        EmitLn, 'MOVE ' + !jcValue + ' (PC),D0' ; a variable
    endelse
end

; ---------------------------------------------------------------------
; Parse and Translate a Math Factor
pro Factor
    if !jcLook eq '(' then begin
        Match, '('
        Expression
        Match, ')'
    endif else if IsAlpha(!jcLook) then begin
        Ident
    endif else begin
        GetNum
        EmitLn, 'MOVE #' + !jcValue + ',D0'
    endelse
end

; ---------------------------------------------------------------------
; Parse and Translate the First Math Factor
pro SignedFactor
    isNeg = !jcLook eq '-'
    if IsAddop(!jcLook) then begin
        GetChar
        SkipWhite
    endif
    Factor
    if isNeg then EmitLn, 'NEG D0'
end

; ---------------------------------------------------------------------
; Recognize and Translate a Multiply
pro Multiply
    Match, '*'
    Factor
    EmitLn, 'MULS (SP)+,D0'
end

; ---------------------------------------------------------------------
; Recognize and Translate a Divide
pro Divide
    Match, '/'
    Factor
    EmitLn, 'MOVE (SP)+,D1'
    EmitLn, 'EXS.L D0'
    EmitLn, 'DIVS D1,D0'
end

; ---------------------------------------------------------------------
; Completion of Term Processing (called by Term and First Term)
pro Term1
    while IsMulop(!jcLook) do begin
        EmitLn, 'MOVE D0,-(SP)'
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
; Parse and Translate a Math Term with Possible Leading Sign
pro FirstTerm
    SignedFactor
    Term1
end

; ---------------------------------------------------------------------
; Recognize and Translate an Add
pro Add
    Match, '+'
    Term
    EmitLn, 'ADD (SP)+,D0'
end

; ---------------------------------------------------------------------
; Recognize and Translate a Subtract
pro Subtract
    Match, '-'
    Term
    EmitLn, 'SUB (SP)+,D0'
    EmitLn, 'NEG D0'
end

; ---------------------------------------------------------------------
; Parse and Translate an Expression
pro Expression
    FirstTerm;
    while IsAddop(!jcLook) do begin
        EmitLn, 'MOVE D0,-(SP)'
        case !jcLook of
            '+': Add
            '-': Subtract
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Boolean Condition
; This version is a dummy
pro Condition
    EmitLn, 'Condition'
end

; ---------------------------------------------------------------------
pro DoIf
    Condition
    L1 = NewLabel()
    L2 = L1
    EmitLn, 'BEQ ' + L1
    Block
    if !jcToken eq 'l' then begin
        L2 = NewLabel()
        EmitLn, 'BRA ' + L2
        PostLabel, L1
        Block;
    endif
    PostLabel, L2
    MatchString, 'ENDIF'
end

; ---------------------------------------------------------------------
; Parse and Translate an Assignment Statement
pro Assignment
    Name = !jcValue
    Match, '='
    Expression
    EmitLn, 'LEA ' + Name + ' (PC),A0'
    EmitLn, 'MOVE D0,(A0)'
end

; ---------------------------------------------------------------------
; Recognize and Translate a Statement Block
pro Block
    Scan
    while where(['e','l'] eq !jcToken) eq -1 do begin
        case !jcToken of
            'i': DoIf
            else: Assignment
        endcase
        Scan
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Program
pro DoProgram
    Block
    MatchString, 'END'
    EmitLn, 'END'
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

    ; Define the Keyword table
    defsysv, '!jcKWlist', exists=e
    if e then !jcKWlist=strarr(100) else defsysv, '!jcKWlist', strarr(100)
    (!jcKWlist)[1:4] = ['IF', 'ELSE', 'ENDIF', 'END']

    ; Define the KWcode
    defsysv, '!jcKWcode', exists=e
    if e then !jcKWcode='xilee' else defsysv, '!jcKWcode', 'xilee'

    GetChar, /newInput
end


; ---------------------------------------------------------------------
; Main Program 
pro jcCompiler

    Init

    DoProgram
    
end


; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version in the middle of chapter that finished the 
; boolean Expressions but before the addition of control struct.
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
;   Last modified: ywang @ Mon 03 Jun 2013
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
; Recognize a Boolean Literal
function IsBoolean, c
    void = where(['T', 'F'] eq strupcase(c), count)
    if count gt 0 then return, 1 else return, 0 
end

; ---------------------------------------------------------------------
; Recognize a Boolean Orop
function IsOrOp, c
    void = where(['|','~'] eq c, count)
    if count gt 0 then return, 1 else return, 0
end

; ---------------------------------------------------------------------
; Recognize a Relop
function IsRelop, c
    void = where(['=','#','<','>'] eq c, count)
    return, count
end

; ---------------------------------------------------------------------
; Recognize a Addop
function IsAddop, c
    void = where(['+','-'] eq c, count)
    return, count
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
; Get a Boolean Literal
function GetBoolean
    if ~IsBoolean(!jcLook) then Expected, 'Boolean Literal'
    theValue = strupcase(!jcLook) eq 'T'
    GetChar
    return, theValue
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
; Recognize and Translate a Relational "Equals"
pro Equals
    Match, '='
    Expression
    EmitLn, 'CMP (SP)+,D0'
    EmitLn, 'SEQ D0'
end

; --------------------------------------------------------------------- 
; Recognize and Translate a Relational "Not Equals"
pro NotEquals
    Match, '#'
    Expression
    EmitLn, 'CMP (SP)+,D0'
    EmitLn, 'SNE D0'
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Less Than"
pro Less
    Match, '<'
    Expression
    EmitLn, 'CMP (SP)+,D0'
    EmitLn, 'SGE D0'
end

; ---------------------------------------------------------------------
; Recognize and Translate a Relational "Greater Than"
pro Greater
    Match, '>'
    Expression
    EmitLn, 'CMP (SP)+,D0'
    EmitLn, 'SLE D0'
end

; ---------------------------------------------------------------------
; Recognize and Translate a Boolean OR
pro BoolOr
    Match, '|'
    BoolTerm
    EmitLn, 'OR (SP)+,D0'
end

; ---------------------------------------------------------------------
; Recognize and Translate and Exclusive Or
pro BoolXor
    Match, '~'
    BoolTerm
    EmitLn, 'EOR (SP)+,D0'
end

; ---------------------------------------------------------------------
; Parse and Translate a Relation
pro Relation
    Expression
    if IsRelop(!jcLook) then begin
        EmitLn, 'MOVE D0,-(SP)'
        case !jcLook of
            '=': Equals
            '#': NotEquals
            '<': Less
            '>': Greater
        endcase
        EmitLn, 'TST D0'
    endif
end


; ---------------------------------------------------------------------
; Parse and Translate a Boolean Factor
pro BoolFactor
    if IsBoolean(!jcLook) then begin
        if GetBoolean() then begin
            EmitLn, 'MOVE #-1,D0'
        endif else begin
            EmitLn, 'CLR D0'
        endelse
    endif else begin
        Relation
    endelse
end


; ---------------------------------------------------------------------
; Parse and Translate a Boolean Factor with NOT
pro NotFactor
    if !jcLook eq '!' then begin
        Match, '!'
        BoolFactor
        EmitLn, 'EOR #-1,D0'
    endif else begin
        BoolFactor
    endelse
end


; ---------------------------------------------------------------------
; Parse and Translate a Boolean Term
pro BoolTerm
    NotFactor
    while !jcLook eq '&' do begin
        EmitLn, 'MOVE D0,-(SP)'
        Match, '&'
        NotFactor
        EmitLn, 'AND (SP)+,D0'
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Boolean Expression
pro BoolExpression
    BoolTerm
    while IsOrOp(!jcLook) do begin
        EmitLn, 'MOVE D0,-(SP)'
        case !jcLook of 
            '|': BoolOr
            '~': BoolXor
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate an Identifier
pro Ident
    name = GetName()
    if !jcLook eq '(' then begin
        ; Function call
        Match, '('
        Match, ')'
        EmitLn, 'BSR ' + name
    endif else begin
        ; Variable
        EmitLn, 'MOVE ' + name + ' (PC),D0'
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
        EmitLn, 'MOVE #'+GetNum()+',D0'
    endelse

end

; ---------------------------------------------------------------------
; Parse and Translate the First Math Factor
pro SignedFactor
    if !jcLook eq '+' then begin
        GetChar
    endif else if !jcLook eq '-' then begin
        GetChar
        if IsDigit(!jcLook) then begin
            EmitLn, 'MOVE #-' + GetNum() + ',D0'
        endif else begin
            Factor
            EmitLn, 'NEG D0'
        endelse
    endif else begin
        Factor
    endelse
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
; Parse and Translate a Math Term
pro Term
    SignedFactor
    while where(['*','/'] eq !jcLook,count) ne -1 do begin
        EmitLn, 'MOVE D0,-(SP)'
        case !jcLook of
            '*': Multiply
            '/': Divide
        end
    endwhile
end

; ---------------------------------------------------------------------
; Recognize and Translate an Add
pro Add
    Match, '+'
    Term
    EmitLn, 'ADD (SP)+,D0'
end

; ---------------------------------------------------------------------
; Recognize and Translate a Substract
pro Subtract
    Match, '-'
    Term
    EmitLn, 'SUB (SP)+,D0'
    EmitLn, 'NEG D0'
end

; ---------------------------------------------------------------------
; Parse and Translate an Expression
pro Expression
    Term
    while IsAddop(!jcLook) do begin
        EmitLn, 'MOVE D0,-(SP)'
        case !jcLook of
            '+': Add
            '-': Subtract
        endcase
    endwhile
end

; --------------------------------------------------------------------- 
; Initialize 

pro Init
    GetChar, /newInput
end


; ---------------------------------------------------------------------
; Main Program 
pro jcCompiler

    defsysv, '!jcLineBuffer', exists=e
    if e then !jcLineBuffer='' else defsysv, '!jcLineBuffer', ''
    ; Define the global available Lookahead Character
    defsysv, '!jcLook', exists=e
    if e then !jcLook='' else defsysv, '!jcLook', '' 

    Init
    BoolExpression
    
end
; --------------------------------------------------------------------- 


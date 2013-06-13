; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
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
;   Last modified: ywang @ Thu 30 May 2013
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
; Recongnize an Addop

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
    theName = GetName()
    if !jcLook eq '(' then begin
        Match, '('
        Match, ')'
        EmitLn, 'BSR ' + theName
    endif else begin
        EmitLn, 'MOVE ' + theName + '(PC),D0'
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
        EmitLn, 'MOVE #' + GetNum() + ',D0'
    endelse
end

; --------------------------------------------------------------------- 
; Recongnize and Translate a Multiply

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
    EmitLn, 'DIVS D1,D0'
end

; --------------------------------------------------------------------- 
; Parse and Translate a Math Term

pro Term
    Factor
    while where(['*','/'] eq !jcLook) ne -1 do begin
        EmitLn, 'MOVE D0,-(SP)'
        case !jcLook of
            '*': Multiply
            '/': Divide
            else: Expected, 'Mulop'
        endcase
    endwhile
end


; --------------------------------------------------------------------- 
; Parse and Translate an Expression

pro Expression;
    if IsAddop(!jcLook) then begin
        EmitLn, 'CLR D0'
    endif else begin
        Term;
    endelse
    while IsAddop(!jcLook) do begin
        EmitLn, 'MOVE D0,-(SP)'
        case !jcLook of
            '+': Add;
            '-': Subtract;
            else: Expected, 'Addop'
        endcase
    endwhile
end;

; --------------------------------------------------------------------- 
; Parse and Translate an Assignment Statement

pro Assignment
    theName = GetName()
    Match, '='
    Expression
    EmitLn, 'LEA ' + theName + '(PC),A0'
    EmitLn, 'MOVE D0,(A0)'
end

; --------------------------------------------------------------------- 
; Recognize and Translate an Add 

pro Add;
    Match, '+'
    Term;
    EmitLn, 'ADD (SP)+,D0'
end;


; --------------------------------------------------------------------- 
; Recognize and Translate a Subtract 

pro Subtract;
    Match, '-'
    Term;
    EmitLn, 'SUB (SP)+,D0'
    EmitLn, 'NEG D0'
end;


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
    ;Expression
    Assignment
    if !jcLook ne '' then Expected, 'Newline'
end
; --------------------------------------------------------------------- 


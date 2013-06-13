; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This the Interpreter version at the end of chapter 4.
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
;   Last modified: ywang @ Fri 31 May 2013
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
; Input Routine
pro Input
    Match, '?'
    aNum = 0
    read, aNum, prompt='Please Enter: '
    Table = !jcTable
    Table[GetName()] = aNum
end

; --------------------------------------------------------------------- 
; Output Routine

pro Output
    Match, '!'
    Table = !jcTable
    printf, -2, Table[GetName()]
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
    theValue = 0
    while IsDigit(!jcLook) do begin
        theValue = 10*theValue + fix(!jcLook)
        GetChar
    endwhile
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
; Parse and Translate an Expression

function Expression
    if IsAddop(!jcLook) then begin
        theValue = 0
    endif else begin
        theValue = Term()
    endelse
    while IsAddop(!jcLook) do begin
        case !jcLook of
            '+': begin
                Match, '+'
                theValue += Term()
            end
            '-': begin
                Match, '-'
                theValue -= Term()
            end
        endcase
    endwhile
    return, theValue
end


; --------------------------------------------------------------------- 
; Parse and Translate a Math Factor 

function Factor
    if !jcLook eq '(' then begin
        Match, '('
        theFactor = Expression()
        Match, ')'
    endif else if IsAlpha(!jcLook) then begin
        theFactor = (!jcTable)[GetName()]
    endif else begin
        theFactor = GetNum()
    endelse
    return, theFactor
end

; --------------------------------------------------------------------- 
; Parse and Translate a Math Term

function Term
    theValue = Factor()
    while where(['*', '/'] eq !jcLook) ne -1 do begin
        case !jcLook of
            '*': begin
                Match, '*'
                theValue *= Factor()
            end
            '/': begin
                Match, '/'
                theValue /= Factor()
            end
        endcase
    endwhile
    return, theValue
end;

; --------------------------------------------------------------------- 
; Parse and Translate an Assignment Statement
                             
pro Assignment
    Name = GetName()
    Match, '='
    Table = !jcTable
    Table[Name] = Expression()
end

; --------------------------------------------------------------------- 
; Initialize the Variable Area

pro InitTable
    theTable = !jcTable
    for ii=65B,90B do begin
       theKey = string(byte(ii))
       theTable[theKey] = 0
    endfor
end


; --------------------------------------------------------------------- 
; Initialize 

pro Init
    InitTable
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

    defsysv, '!jcTable', exists=e
    if e then !jcTable=hash() else defsysv, '!jcTable', hash()

    Init
    repeat begin
        case !jcLook of
            '?': Input
            '!': Output
            else: Assignment
        endcase
        if !jcLook eq '' and !jcLineBuffer eq '' then GetChar, /newInput
    endrep until !jcLook eq '.'

end
; --------------------------------------------------------------------- 


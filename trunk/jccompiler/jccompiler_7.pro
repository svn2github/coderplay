; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version in the middle of Tutor 7, which implements
; a scanner with single character coded Token Type and allow for 
; multiple line inputs.
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
; Recognize an Alphanumeric Character
function IsAlNum, c
    return, IsAlpha(c) or IsDigit(c)
end

; ---------------------------------------------------------------------
; Recognize Any Operator
function IsOp, c
    void = where(['+','-','*','/','<','>',':','='] eq c, count)
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
    if ~IsAlpha(!jcLook) then Expected, 'Name'
    value = ''
    while IsAlNum(!jcLook) do begin
        value += strupcase(!jcLook);
        GetChar
    endwhile
    SkipWhite
    !jcToken = strmid(!jcKWcode, Lookup(!jcKWlist, value, 4), 1);
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
; Get an Op
pro GetOp
    if ~IsOp(!jcLook) then Expected, 'Operator'
    value = ''
    while IsOp(!jcLook) do begin
        value += !jcLook
        GetChar
    endwhile
    SkipWhite
    if strlen(value) eq 1 then begin
        !jcToken = value
    endif else begin
        !jcToken = '?'
    endelse
    !jcValue = value
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
; Lexical Scanner
pro Scan
    if !jcLook eq '' then GetChar, /newInput
    if IsAlpha(!jcLook) then begin
        GetName
    endif else if IsDigit(!jcLook) then begin
        GetNum
    endif else if IsOp(!jcLook) then begin
        GetOp
    endif else begin
        !jcValue = !jcLook
        !jcToken = '?'
        GetChar
    endelse
    SkipWhite
end

; --------------------------------------------------------------------- 
; Initialize 

pro Init
    defsysv, '!jcLineBuffer', exists=e
    if e then !jcLineBuffer='' else defsysv, '!jcLineBuffer', ''
    ; Define the global available Lookahead Character
    defsysv, '!jcLook', exists=e
    if e then !jcLook='' else defsysv, '!jcLook', '' 

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
    repeat begin
        Scan
        switch !jcToken of
            'x': begin
                print, 'Ident ', format='(A,$)'
                break
            end
            '#': begin
                print, 'Number ', format='(A,$)'
                break
            end
            'i':
            'l':
            'e': begin
                print, 'Keyword ', format='(A,$)'
                break
            end
            else: begin
                print, 'Operator ', format='(A,$)'
            end
        endswitch
        print, !jcValue
    endrep until !jcValue eq 'END'
    
end
; --------------------------------------------------------------------- 


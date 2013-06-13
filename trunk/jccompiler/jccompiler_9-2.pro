; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version at the end of Chapter 9, which features a C 
; parser example.
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
pro GetClass
    if where(['a', 'x', 's'] eq !jcLook) ne -1 then begin
        !jcClass = !jcLook
        GetChar
    endif else begin
        !jcClass = 'a'
    endelse
end

; ---------------------------------------------------------------------
; Get a Type Specifier
pro GetType
    !jcTyp = ' '
    if !jcLook eq 'u' then begin
        !jcSign = 'u'
        !jcTyp = 'i'
        GetChar
    endif else begin
        !jcSign = 's'
        if where(['i','l','c'] eq !jcLook) ne -1 then begin
            !jcTyp = !jcLook
            GetChar
        endif 
    endelse
end

; ---------------------------------------------------------------------
; Process a Function Definition
pro DoFunc, n
    Match, '('
    Match, ')'
    Match, '{'
    Match, '}'
    if !jcTyp eq ' ' then !jcType = 'i'
    print, !jcClass, !jcSign, !jcTyp, ' function ', n
end

; ---------------------------------------------------------------------
; Process a Data Declaration
pro DoData, n
    if !jcTyp eq ' ' then Expected, 'Type declaration'
    print, !jcClass, !jcSign, !jcTyp, ' data ', n
    while !jcLook eq ',' do begin
        Match, ','
        n = GetName()
        print, !jcClass, !jcSign, !jcTyp, ' data ', n
    endwhile
    Match, ';'
end

; ---------------------------------------------------------------------
; Process a Top-Level Declaration
pro TopDecl
    Name = GetName()
    if !jcLook eq '(' then begin
        DoFunc, Name
    endif else begin
        DoData, Name
    endelse
end

; --------------------------------------------------------------------- 
; Initialize 

pro Init

    defsysv, '!jcLineBuffer', exists=e
    if e then !jcLineBuffer='' else defsysv, '!jcLineBuffer', ''
    ; Define the global available Lookahead Character
    defsysv, '!jcLook', exists=e
    if e then !jcLook='' else defsysv, '!jcLook', '' 

    defsysv, '!jcClass', exists=e
    if e then !jcClass='' else defsysv, '!jcClass', '' 
    defsysv, '!jcSign', exists=e
    if e then !jcSign='' else defsysv, '!jcSign', '' 
    defsysv, '!jcTyp', exists=e
    if e then !jcTyp='' else defsysv, '!jcTyp', '' 

    GetChar, /newInput
end


; ---------------------------------------------------------------------
; Main Program 
pro jcCompiler

    Init
    while !jcLook ne '' do begin
        GetClass
        GetType
        TopDecl
    endwhile
    
end
; --------------------------------------------------------------------- 


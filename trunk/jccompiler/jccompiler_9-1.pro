; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version for the top down Pascal parser in Chapter 9.
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
; Process Label Statement
pro Labels
    Match, 'l'
end

; ---------------------------------------------------------------------
; Process Constants Statement
pro Constants
    Match, 'c'
end

; ---------------------------------------------------------------------
; Process Types Statement
pro Types
    Match, 't'
end

; ---------------------------------------------------------------------
; Process Var Statement
pro Variables
    Match, 'v'
end

; ---------------------------------------------------------------------
; Process Procedure Statement
pro DoProcedures
    Match, 'p'
end

; ---------------------------------------------------------------------
; Process Function Statement
pro DoFunction
    Match, 'f'
end

; ---------------------------------------------------------------------
; Parse and Translate the Statement Part
pro Statements
    match, 'b'
    while !jcLook ne 'e' do begin
        GetChar
    endwhile
    Match, 'e'
end

; ---------------------------------------------------------------------
; Parse and Translate the Declaration Part
pro Declarations
    while where(['l','c','t','v','p','f'] eq !jcLook) ne -1 do begin
        case !jcLook of
            'l': Labels
            'c': Constants
            't': Types
            'v': Variables
            'p': DoProcedures
            'f': DoFunction
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Pascal Block
pro DoBlock, Name
    Declarations
    PostLabel, Name
    Statements
end

; ---------------------------------------------------------------------
; Write the Prolog
pro Prolog, Name
    EmitLn, 'WARMST EQU $A01E'
end

; ---------------------------------------------------------------------
; Write the Epilog
pro Epilog, Name
    EmitLn, 'DC WARMST'
    EmitLn, 'END ' + Name
end

; ---------------------------------------------------------------------
; Parse and Translate A Program
pro Prog
    Match, 'p'
    Name = GetName()
    Prolog, Name
    DoBlock, Name
    Match, '.'
    Epilog, Name
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

    GetChar, /newInput
end


; ---------------------------------------------------------------------
; Main Program 
pro jcCompiler

    Init
    Prog

end
; --------------------------------------------------------------------- 


; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version with control struct at the end of chapter 5.
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
;   Last modified: ywang @ Sat 01 Jun 2013
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
; Parse and Translate a Boolean Condition
; This version is a dummy
pro Condition
    EmitLn, '<condition>'
end

; ---------------------------------------------------------------------
; Parse and Translate an Expression
; This version is a dummy

pro Expression
    EmitLn, '<expr>'
end

; ---------------------------------------------------------------------
; Recognize and Translate a BREAK
pro DoBreak, L
    Match, 'b'
    if L ne '' then begin
        EmitLn, 'BRA '+L
    endif else begin
        Abort, 'No loop to break from'
    endelse
end

; ---------------------------------------------------------------------
; Parse and Translate a DO Statement
pro Dodo
    Match, 'd'
    L1 = NewLabel()
    L2 = NewLabel()
    Expression
    EmitLn, 'SUBQ #1,D0'
    PostLabel, L1
    EmitLn, 'MOVE D0,-(SP)'
    Block, L2
    Match, 'e'
    EmitLn, 'MOVE (SP)+,D0'
    EmitLn, 'DBRA D0,' + L1
    EmitLn, 'SUBQ #2,SP'
    PostLabel, L2
    EmitLn, 'ADDQ #2,SP'
end


; ---------------------------------------------------------------------
; Parse and Translate a FOR Statement
pro DoFor
    Match, 'f'
    L1 = NewLabel()
    L2 = NewLabel()
    name = GetName()
    Match, '='
    Expression
    EmitLn,'SUBQ #1,D0'
    EmitLn,'LEA ' + Name + '(PC),A0'
    EmitLn,'MOVE D0,(A0)'
    Expression
    EmitLn,'MOVE D0,-(SP)'
    PostLabel,L1
    EmitLn,'LEA ' + Name + '(PC),A0'
    EmitLn,'MOVE (A0),D0'
    EmitLn,'ADDQ #1,D0'
    EmitLn,'MOVE D0,(A0)'
    EmitLn,'CMP (SP),D0'
    EmitLn,'BGT ' + L2
    Block, L2
    Match, 'e'
    EmitLn,'BRA ' + L1
    PostLabel,L2;
    EmitLn,'ADDQ #2,SP'
end

; ---------------------------------------------------------------------
; Parse and Translate a REPEAT Statement
pro DoRepeat
    Match, 'r'
    L1 = NewLabel()
    L2 = NewLabel()
    PostLabel, L1
    Block, L2
    Match, 'u'
    Condition
    EmitLn, 'BEQ '+L1
    PostLabel, L2
end

; ---------------------------------------------------------------------
; Parse and Translate a LOOP Statement
pro DoLoop
    Match, 'p'
    L1 = NewLabel()
    L2 = NewLabel()
    PostLabel, L1
    Block, L2
    Match, 'e'
    EmitLn, 'BRA ' + L1
    PostLabel, L2
end


; ---------------------------------------------------------------------
; Parse and Translate a WHILE Statement
pro DoWhile
    Match, 'w'
    L1 = NewLabel()
    L2 = NewLabel()
    PostLabel, L1
    Condition
    EmitLn, 'BEQ '+L2
    Block, L2
    Match, 'e'
    EmitLn, 'BRA '+L1
    PostLabel, L2
end

; ---------------------------------------------------------------------
; Recognize and Translate and IF Construct
pro DoIf, L
    Match, 'i'
    Condition
    L1 = NewLabel()
    L2 = L1
    EmitLn, 'BEQ ' + L1
    Block, L
    if !jcLook eq 'l' then begin
        Match, 'l'
        L2 = NewLabel()
        EmitLn, 'BRA '+L2
        PostLabel, L1
        Block, L
    endif
    Match, 'e'
    PostLabel, L2
end

; ---------------------------------------------------------------------
; Recognize and Translate an "Other"

pro Other
    EmitLn, GetName();
end

; ---------------------------------------------------------------------
; Recognize and Translate a Statement Block

pro Block, L
    while where(['e','l','u'] eq !jcLook, count) eq -1 do begin
        case !jcLook of
            'i': DoIf, L
            'w': DoWhile
            'p': DoLoop
            'r': DoRepeat
            'f': DoFor
            'd': Dodo
            'b': DoBreak, L
            else: Other
        endcase
    endwhile
end

; ---------------------------------------------------------------------
; Parse and Translate a Program

pro DoProgram
    Block, ''
    if !jcLook ne 'e' then Expected, 'End'
    EmitLn, 'END'
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
    
    defsysv, '!jcLcount', exists=e
    if e then !jcLcount=0 else defsysv, '!jcLcount', 0

    Init
    DoProgram
    
end
; --------------------------------------------------------------------- 


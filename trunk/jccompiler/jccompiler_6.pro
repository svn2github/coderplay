; docformat = 'rst'

;+
; The purpose of this file is to translate Jack Crenshaw's tutorial, 
; Let's Build a Compiler,which was orginally written in Turbo Pascal.
; This is the version at the end of chapter 6 with all bool expression
; and control structs.
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
    BoolExpression
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
    BoolExpression
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
    BoolExpression
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
    EmitLn, GetName()
end

; ---------------------------------------------------------------------
; Parse and Translate an Assignment Statement
pro Assignment
    name = GetName()
    Match, '='
    BoolExpression
    EmitLn, 'LEA ' + name + '(PC),A0'
    EmitLn, 'MOVE D0,(A0)'
end

; ---------------------------------------------------------------------
; Recognize and Translate a Statement Block

pro Block, L
    while where(['e','l','u'] eq !jcLook, count) eq -1 do begin
        ; This is some ugly solution to allow multiline statement
        ; It is still a control struct but written in multiple lines.
        if !jcLook eq '' and !jcLineBuffer eq '' then GetChar, /newInput
        case !jcLook of
            'i': DoIf, L
            'w': DoWhile
            'p': DoLoop
            'r': DoRepeat
            'f': DoFor
            'd': Dodo
            'b': DoBreak, L
            else: Assignment
        endcase
        if !jcLook eq '' and !jcLineBuffer eq '' then GetChar, /newInput
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


" Syntax file for the Emma programming language
"
if exists("b:current_syntax")
    finish
endif

syn keyword EmmaStatement   print if elif else while for continue break
syn keyword EmmaStatement   return package import try raise catch finally
syn keyword EmmaStatement   def class nextgroup=EmmaFunction skipwhite
syn match   EmmaFunction    "[a-zA-Z_][a-zA-Z0-9_]*" contained
syn keyword EmmaTypes       null stdout stdin stderr
syn keyword EmmaOperator    and or xor not
syn keyword EmmaToDo        TODO FIXME XXX DEBUG NOTE contained

syn keyword EmmaBuiltin     list hash

syn match   EmmaComments    "#.*$" contains=EmmaToDo

syn region  EmmaString      start=+"+ end=+"+ skip=+\\"+
syn region  EmmaString      start=+'+ end=+'+ skip=+\\'+

hi link EmmaStatement   Statement
hi link EmmaTypes       Type
hi link EmmaOperator    Operator
hi link EmmaComments    Comment
hi link EmmaString      String
hi link EmmaToDo        Todo
hi link EmmaFunction    Function
hi link EmmaBuiltin     Function

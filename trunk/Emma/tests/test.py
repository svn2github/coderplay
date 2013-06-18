"""

>>> test_control_flow_1()
[-->('for', 'FOR')<--, ('ii', 'ID'), ('=', '='), ('1', 'INT'), (',', ','), ('10', 'INT'), ('{', '{'), ('\\n', 'EOL'), ('x', 'ID'), ('=', '='), ('ii', 'ID'), ('\\n', 'EOL'), ('while', 'WHILE'), ('x', 'ID'), ('>', '>'), ('0', 'INT'), ('{', '{'), ('\\n', 'EOL'), ('x', 'ID'), ('=', '='), ('x', 'ID'), ('-', '-'), ('1', 'INT'), ('\\n', 'EOL'), ('if', 'IF'), ('x', 'ID'), ('%', '%'), ('2', 'INT'), ('==', '=='), ('0', 'INT'), ('continue', 'CONTINUE'), ('\\n', 'EOL'), ('print', 'PRINT'), ("'    '", 'STR'), (',', ','), ('x', 'ID'), (',', ','), ('ii', 'ID'), ('\\n', 'EOL'), ('}', '}'), ('\\n', 'EOL'), ('if', 'IF'), ('ii', 'ID'), ('%', '%'), ('2', 'INT'), ('==', '=='), ('0', 'INT'), ('continue', 'CONTINUE'), ('\\n', 'EOL'), ('print', 'PRINT'), ('ii', 'ID'), ('\\n', 'EOL'), ('}', '}'), ('\\n', 'EOL')]
File(Stmt_List(ForLoop(Variable(ii), Int(1), Int(10), Int(1), Stmt_Block(Stmt_List(BinOp(=, Variable(x), Variable(ii))), Stmt_List(WhileLoop(BinOp(>, Variable(x), Int(0)), Stmt_Block(Stmt_List(BinOp(=, Variable(x), BinOp(-, Variable(x), Int(1)))), Stmt_List(If(BinOp(==, BinOp(%, Variable(x), Int(2)), Int(0)), Continue, None)), Stmt_List(Print(String(    ), Variable(x), Variable(ii)))))), Stmt_List(If(BinOp(==, BinOp(%, Variable(ii), Int(2)), Int(0)), Continue, None)), Stmt_List(Print(Variable(ii)))))))
1
     1 2
     1 3
3
     3 4
     1 4
     3 5
     1 5
5
     5 6
     3 6
     1 6
     5 7
     3 7
     1 7
7
     7 8
     5 8
     3 8
     1 8
     7 9
     5 9
     3 9
     1 9
9
     9 10
     7 10
     5 10
     3 10
     1 10


>>> test_control_flow_2()
[-->('for', 'FOR')<--, ('ii', 'ID'), ('=', '='), ('1', 'INT'), (',', ','), ('10', 'INT'), ('{', '{'), ('\\n', 'EOL'), ('x', 'ID'), ('=', '='), ('ii', 'ID'), ('+', '+'), ('5', 'INT'), ('\\n', 'EOL'), ('while', 'WHILE'), ('x', 'ID'), ('>', '>'), ('0', 'INT'), ('{', '{'), ('\\n', 'EOL'), ('x', 'ID'), ('=', '='), ('x', 'ID'), ('-', '-'), ('1', 'INT'), ('\\n', 'EOL'), ('if', 'IF'), ('x', 'ID'), ('<', '<'), ('2', 'INT'), ('break', 'BREAK'), ('\\n', 'EOL'), ('print', 'PRINT'), ("'    '", 'STR'), (',', ','), ('x', 'ID'), (',', ','), ('ii', 'ID'), ('\\n', 'EOL'), ('}', '}'), ('\\n', 'EOL'), ('if', 'IF'), ('ii', 'ID'), ('%', '%'), ('2', 'INT'), ('==', '=='), ('0', 'INT'), ('continue', 'CONTINUE'), ('\\n', 'EOL'), ('if', 'IF'), ('ii', 'ID'), ('==', '=='), ('9', 'INT'), ('break', 'BREAK'), ('\\n', 'EOL'), ('print', 'PRINT'), ('ii', 'ID'), ('\\n', 'EOL'), ('}', '}'), ('\\n', 'EOL')]
File(Stmt_List(ForLoop(Variable(ii), Int(1), Int(10), Int(1), Stmt_Block(Stmt_List(BinOp(=, Variable(x), BinOp(+, Variable(ii), Int(5)))), Stmt_List(WhileLoop(BinOp(>, Variable(x), Int(0)), Stmt_Block(Stmt_List(BinOp(=, Variable(x), BinOp(-, Variable(x), Int(1)))), Stmt_List(If(BinOp(<, Variable(x), Int(2)), Break, None)), Stmt_List(Print(String(    ), Variable(x), Variable(ii)))))), Stmt_List(If(BinOp(==, BinOp(%, Variable(ii), Int(2)), Int(0)), Continue, None)), Stmt_List(If(BinOp(==, Variable(ii), Int(9)), Break, None)), Stmt_List(Print(Variable(ii)))))))
     5 1
     4 1
     3 1
     2 1
1
     6 2
     5 2
     4 2
     3 2
     2 2
     7 3
     6 3
     5 3
     4 3
     3 3
     2 3
3
     8 4
     7 4
     6 4
     5 4
     4 4
     3 4
     2 4
     9 5
     8 5
     7 5
     6 5
     5 5
     4 5
     3 5
     2 5
5
     10 6
     9 6
     8 6
     7 6
     6 6
     5 6
     4 6
     3 6
     2 6
     11 7
     10 7
     9 7
     8 7
     7 7
     6 7
     5 7
     4 7
     3 7
     2 7
7
     12 8
     11 8
     10 8
     9 8
     8 8
     7 8
     6 8
     5 8
     4 8
     3 8
     2 8
     13 9
     12 9
     11 9
     10 9
     9 9
     8 9
     7 9
     6 9
     5 9
     4 9
     3 9
     2 9

"""

def test_control_flow_1():
    from Emma import Emma
    e = Emma()
    e.run_file('tests/1.em')

def test_control_flow_2():
    from Emma import Emma
    e = Emma()
    e.run_file('tests/2.em')


if __name__ == "__main__":
    import doctest
    doctest.testmod()

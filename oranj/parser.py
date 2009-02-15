#!/usr/bin/env python

from __future__ import division

import ply.yacc as yacc
from lexer import tokens, literals
import pprint # Because parse trees get hairy
import sys
import terminal

errors = 0

term = terminal.TerminalController()

start = "statements"

precedence = (
    ("left", "+", "-"),
    ("left", "*", "/", "MOD"),
    ("left", "^"),
    ("left", "MINUSMINUS", "PLUSPLUS"),
    ("right", "UMINUS", "UPLUS"),
)

def p_primitive(p):
    """primitive : DEC
                 | STRING
                 | INT
                 | NIL
                 | BOOL
                 | INF"""

    p[0] = ("PRIMITIVE", p[1])

def p_primitive_IDENT(p):
    """ident : IDENT"""

    p[0] = ("IDENT", p[1])

def p_literal_list(p):
    """literal : '[' list_items ']'
               | '[' list_items ',' ']'
               | '[' ']'"""

    if len(p) == 3:
        p[0] = ("LIST", [])
    else:
        p[0] = ("LIST", p[2])

def p_literal_alist(p):
    """literal : '[' hash_items ']'
               | '[' hash_items ',' ']'"""
    p[0] = ("TABLE", p[2])

def p_literal_set(p):
    """literal : '{' list_items '}'
               | '{' list_items ',' '}'"""
    p[0] = ("SET", p[2])

def p_literal_dict(p):
    """literal : '{' hash_items '}'
               | '{' hash_items ',' '}'
               | '{' '}'"""
    if len(p) == 3:
        p[0] = ("DICT", [])
    else:
        p[0] = ("DICT", p[2])

def p_list_items(p):
    """list_items : list_items ',' expression
                  | expression"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_hash_items(p):
    """hash_items : hash_items ',' primitive ':' expression
                  | hash_items ',' ident ':' expression
                  | primitive ':' expression
                  | ident ':' expression"""

    if len(p) < 5:
        p[0] = [(p[1], p[3])]
    else:
        p[0] = p[1] + [(p[3], p[5])]

def p_test_or(p):
    """test_or : test_or OR test_and
               | test_and"""

    if len(p) == 4:
        p[0] = ("OR", p[1], p[3])
    else:
        p[0] = p[1]

def p_test_and(p):
    """test_and : test_and AND test_not
                | test_not"""

    if len(p) == 4:
        p[0] = ("AND", p[1], p[3])
    else:
        p[0] = p[1]

def p_test_not(p):
    """test_not : NOT test_in
                | test_in"""

    if len(p) == 3:
        p[0] = ("NOT", p[2])
    else:
        p[0] = p[1]

def p_test_in(p):
    """test_in : test_in IN test_type
               | test_in NOT IN test_type
               | test_in '|' test_type
               | test_type"""

    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    elif len(p) == 5:
        p[0] = ("NOT IN", p[1], p[4])
    else:
        p[0] = p[1]

def p_test_type(p):
    """test_type : test_type IS test_comp
                 | test_type IS NOT test_comp
                 | test_comp"""

    if len(p) == 4:
        p[0] = ("IS", p[1], p[3])
    elif len(p) == 5:
        p[0] = ("IS NOT", p[1], p[4])
    else:
        p[0] = p[1]

def p_test_comp(p):
    """test_comp : test_comp '<' test_io
                 | test_comp LE test_io
                 | test_comp '>' test_io
                 | test_comp GE test_io
                 | test_comp NE test_io
                 | test_comp EQ test_io
                 | test_io"""

    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    elif len(p) == 5:
        p[0] = (p[2] + p[3], p[1], p[4])
    else:
        p[0] = p[1]

def p_test_io(p):
    """test_io : test_io LTLT test_pm
               | test_io GTGT test_pm
               | test_pm"""

    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_test_pm(p):
    """test_pm : test_pm '+' test_mdmf
               | test_pm '-' test_mdmf
               | test_mdmf"""

    if len(p) == 4:
        if p[1][0] == "PRIMITIVE" and p[2][0] == "PRIMITIVE":
            a = p[1][1]
            b = p[2][1]
            
            if p[2] == "+":
                c = a+b
            elif p[2] == "-":
                c = a-b
            p[0] = ("PRIMITIVE", c)
            return
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_test_mdmf(p):
    """test_mdmf : test_mdmf '*' test_un
                 | test_mdmf '/' test_un
                 | test_mdmf SLASHSLASH test_un
                 | test_mdmf MOD test_un
                 | test_un"""

    if len(p) > 2:
        if p[1][0] == "PRIMITIVE" and p[2][0] == "PRIMITIVE":
            a = p[1][1]
            b = p[2][1]
            
            if p[2] == "*":
                c = a*b
            elif p[2] == "/":
                c = a/b
            elif p[2] == "//":
                c = a//b
            else:
                c = a % b

            p[0] = ("PRIMITIVE", c)
            return
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_test_un(p):
    """test_un : test_un PLUSPLUS
               | test_un MINUSMINUS
               | '-' test_un %prec UMINUS
               | '+' test_un %prec UPLUS
               | test_exp"""

    if len(p) == 3 and p[2] in ("++", "--"):
        p[0] = (p[2], p[1])
    elif p[1] in ("+", "-"):
        p[0] = ("U"+p[1], p[2])
    else:
        p[0] = p[1]

def p_test_exp(p):
    """test_exp : test_call '^' test_exp
                | test_call"""

    if len(p) == 4:
        if p[1][0] == "PRIMITIVE" and p[2][0] == "PRIMITIVE":
            p[0] = ("PRIMTIVE", p[1][1] ** p[2][1])
        else:
            p[0] = ("^", p[1], p[3])
    else:
        p[0] = p[1]

def p_test_call(p):
    """test_call : test_call '(' arglist ')'
                 | test_call '(' arglist ',' ')'
                 | test_attr"""

    if len(p) >= 5:
        p[0] = tuple(["CALL", p[1]] + p[3])
    else:
        p[0] = p[1]

def p_arglist(p):
    """arglist : arglist ',' arg
               | arg
               |"""

    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_arg(p):
    """arg : expression
           | ident '=' expression
           | '*' ident
           | '*' '*' ident"""

    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        if p[1] == "*":
            p[0] = ("UNWRAPKW", p[3])
        else:
            p[0] = ("KW", p[1], p[3])
    else:
        p[0] = ("UNWRAP", p[2])

def p_test_attr(p):
    """test_attr : test_attr '.' test_sub
                 | test_sub"""

    if len(p) == 4:
        p[0] = ("ATTR", p[1], p[3])
    else:
        p[0] = p[1]

def p_test_sub(p):
    """test_sub : test_sub '[' index ']'
                | test_sub '[' index ',' ']'
                | test_basis"""

    if len(p) >= 5:
        if len(p[3]) == 1:
            p[3] = p[3][0]
        p[0] = ("INDEX", p[1], p[3])
    else:
        p[0] = p[1]

def p_index(p):
    """index : index ',' indice
             | indice"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_indice(p):
    """indice : expression ':' expression ':' expression
              | expression ':' expression
              | expression
              | DOTDOTDOT
              |"""
    if len(p) == 6:
        p[0] = ("SLICE", p[1], p[3], p[5]) # TODO: Slice class
    elif len(p) == 4:
        p[0] = ("SLICE", p[1], p[3])
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None

def p_test_basis(p):
    """test_basis : primitive
                  | literal
                  | ident""" # Should be ident, but god hates you
    
    if type(p[1]) == type([]):
        p[1] = p[1][0]

    p[0] = p[1]

def p_test_basis_paren(p):
    """test_basis : '(' expression ')'"""

    p[0] = p[2]

def p_expression_test(p):
    """expression : test_or"""

    p[0] = p[1]

# Rules that end in _s are statements

def p_statement(p):
    """statement : expression
                     | var_s
                     | flow_s
                     | assert_s
                     | block_s
                     | import_s
                     | assignment
                     | declaration"""

    p[0] = p[1]

def p_assignment(p):
    """assignment : many_idents EQOP comma_list"""

    if len(p[1]) < len(p[3]):
        raise yacc.SyntaxError

    p[0] = (p[2], p[1], p[3])

def p_declaration(p):
    """declaration : ident assignment"""

    p[0] = ("DECLARE", p[1], p[2])

def p_var_s(p):
    """var_s : DEL many_idents
             | EXTERN many_idents"""

    p[0] = (p[1].upper(), p[2])

def p_many_idents(p):
    """many_idents : many_idents ',' ident
                   | ident"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_flow_s(p):
    """flow_s : BREAK flow_item
              | CONTINUE flow_item
              | RETURN comma_list
              | RETURN comma_list ','
              | THROW flow_item
              | YIELD comma_list
              | YIELD comma_list ','"""

    p[0] = (p[1].upper(), p[2])

def p_flow_item(p):
    """flow_item : expression
                 |"""

    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None

def p_comma_list(p):
    """comma_list : comma_list ',' expression
                  | expression"""
    
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_import_s(p):
    """import_s : IMPORT import_items
                | IMPORT import_items AS ident"""

    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = (p[1], p[2], p[3])

def p_import_items(p):
    """import_items : ident '.' import_items
                    | ident
                    | '*'"""

    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif p[1] != "*":
        p[0] = [p[1]]
    else:
        p[0] = ["* ANY"]

def p_assert_s(p):
    """assert_s : ASSERT expression
                | ASSERT expression ',' expression"""

    if len(p) == 3:
        p[0] = ("ASSERT", p[2])
    else:
        p[0] = ("ASSERT", p[2], p[4])

def p_block_s(p):
    """block_s : if_s
               | while_s
               | for_s
               | try_s"""
#               | with_s
#               | class_s
#               | fn_s"""

#TODO: with, class, and fn statements

    p[0] = p[1]

def p_if_s(p):
    """if_s : if_if if_elifs else"""

    p[0] = tuple(p[1] + p[2] + p[3])

def p_if_if(p):
    """if_if : IF expression block"""

    p[0] = ["IF", p[2], p[3]]

def p_if_elif(p):
    """if_elifs : ELIF expression block if_elifs
                |"""

    if len(p) == 1:
        p[0] = []
    else:
        p[0] = ["ELIF", p[2], p[3]] + p[4]

def p_else(p):
    """else : ELSE block
            |"""

    if len(p) == 1:
        p[0] = []
    else:
        p[0] = ["ELSE", p[2]]

def p_block(p):
    """block : '{' statements '}'"""
    
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_while_s(p):
    """while_s : WHILE expression block else
               | WHILE block else"""

    if len(p) == 5:
        p[0] = tuple(["WHILE", p[2], p[3]] + p[4])
    else:
        p[0] = tuple(["WHILE", p[2]] + p[3])

def p_for_s(p):
    """for_s : FOR many_idents IN comma_list block else"""

    p[0] = tuple(["FOR", (p[2], p[4]), p[5]] + p[6])

def p_try_s(p):
    """try_s : try_try try_catch else"""

    p[0] = tuple(p[1] + p[2] + p[3])

def p_try_try(p):
    """try_try : TRY block"""

    p[0] = ["TRY", p[2]]

def p_try_catch(p):
    """try_catch : CATCH expression block try_catch
                 | CATCH expression AS ident block try_catch
                 |"""

    if len(p) == 1:
        p[0] = []
    elif len(p) == 5:
        p[0] = ["CATCH", p[2], p[3]] + p[4]
    else:
        p[0] = ["CATCH", p[2], p[4], p[5]] + p[6]

def p_statements(p):
    """statements : statements NEWLINE
                  | statements NEWLINE statement
                  | statement
                  | """

    if len(p) == 1:
        p[0] = []
    elif len(p) in (2, 3):
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_error(t):
    global errors

    try:
        print term.render("${RED}SyntaxError (line %d, col %d):${NORMAL} The %s confuses me" % (t.lineno, t.lexpos + 1, repr(t.value).lower()))
    except AttributeError:
        print term.render("${RED}SyntaxError${NORMAL}")

    errors += 1

yacc.yacc()

def parse(s):
    global errors
    errors = 0


    r = yacc.parse(s)
    try:
        r = yacc.parse(s)
    except:
        raise Exception("Parsing error occurred")
    if errors: raise Exception("Parsing error occurred")
    return r

def _test(s):
    global errors
    y = parse(s)
    
    if type(y) == type([]) and len(y) > 1:
        errors += 1

    if errors:
        print term.render("${RED}${BOLD}%d error%s" % (errors, "s" if errors > 1 else ""))
    else:
        pprint.pprint(y[0])

if __name__ == "__main__":
    if len(sys.argv) == 2:
        y = parse(open(sys.argv[1]).read())
    else:
        try:
            while True:
                _test(raw_input("parse> ") + "\n")
        except (EOFError, KeyboardInterrupt):
            print

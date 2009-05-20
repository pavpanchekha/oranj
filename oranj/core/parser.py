#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ply.yacc as yacc
import ply.lex as lex
from lexer import tokens, literals

import terminal
class ParseError(Exception): pass
term = terminal.TerminalController()

start = "statements"
precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("right", "NOT"),
    ("left", "IN", "|", "NOTIN"),
    ("left", "IS", "ISNT"),
    ("left", "LE", "GE", "NE", "EQ", "<", ">"),
    ("left", "LTLT", "GTGT"),
    ("left", "-", "+"),
    ("left", "SLASHSLASH", "MOD", "/", "*"),
    ("left", "PLUSPLUS", "MINUSMINUS"),
    ("right", "UMINUS"),
    ("right", "^"),
    ("left", "!"),
    ("left", ".", "(", ")", "[", "]"),
)

def p_string(p):
    """string : STRING string
              | STRING"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_primitive(p):
    """primitive : DEC
                 | INT
                 | NIL
                 | BOOL
                 | INF"""
    p[0] = ["PRIMITIVE", p[1]]

def p_primitive_str(p):
    """primitive : string"""

    p[0] = ["STRING", p[1]]

def p_expr_bin(p):
    """expr : expr OR expr
            | expr AND expr
            | expr IN expr
            | expr '|' expr
            | expr IS expr
            | expr LE expr
            | expr '<' expr
            | expr '>' expr
            | expr GE expr
            | expr NE expr
            | expr EQ expr
            | expr LTLT expr
            | expr GTGT expr
            | expr '+' expr
            | expr '-' expr
            | expr '*' expr
            | expr '/' expr
            | expr SLASHSLASH expr
            | expr MOD expr
            | expr '^' expr"""

    p[0] = ["OP", p[2].upper(), p[1], p[3]]

def p_expr_postcall(p):
    """expr : expr '!' expr"""

    if p[3][0] == "CALL":
        t = p[3][:]
        t.insert(2, p[1])
        p[0] = t
    else:
        p[0] = ["CALL", p[3], p[1]]

def p_lvalue_attr(p):
    """lvalue : expr '.' IDENT"""

    p[0] = ["GETATTR", p[1], p[3]]

def p_lvalue_call(p):
    """lvalue : expr '(' arglist ')'
              | expr '(' arglist ',' ')'"""

    p[0] = ["CALL", p[1]] + p[3]

def p_arglist(p):
    """arglist : arglist ',' arg
               | arg
               | """

    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_arg_expr(p):
    """arg : expr"""
    p[0] = p[1]

def p_arg_kw(p):
    """arg : IDENT ASSIGN expr"""
    p[0] = ["KW", p[1], p[3]]

def p_arg_mult(p):
    """arg : '*' expr"""
    p[0] = ["UNWRAP", p[2]]

def p_arg_kwmult(p):
    """arg : '*' '*' expr"""
    p[0] = ["UNWRAPKW", p[3]]

def p_lvalue_index(p):
    """lvalue : expr '[' index ']'
              | expr '[' index ',' ']'"""

    p[0] = ["OP", "GETINDEX", p[1], p[3]]

def p_index(p):
    """index : index ',' indice
             | indice"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_indice3(p):
    """indice : expr ':' expr ':' expr
              | ':' expr ':' expr
              | expr ':' ':' expr
              | ':' ':' expr"""

    if len(p) == 6:
        p[0] = ["SLICE", p[1], p[3], p[5]]
    elif len(p) == 5 and p[1] == ":":
        p[0] = ["SLICE", ["PRIMITIVE", ["INT", "0", 10]], p[2], p[4]]
    elif len(p) == 5:
        p[0] = ["SLICE", p[1], ["PRIMITIVE", ["INT", "-1", 10]], p[4]]
    else:
        p[0] = ["SLICE", ["PRIMITIVE", ["INT", "0", 10]], ["PRIMITIVE", ["INT", "-1", 10]], p[3]]

def p_indice2(p):
    """indice : expr ':' expr
              | ':' expr
              | expr ':'
              | ':'"""

    if len(p) == 4:
        p[0] = ["SLICE", p[1], p[3]]
    elif p[1] == ":" and len(p) == 3:
        p[0] = ["SLICE", ["PRIMITIVE", ["INT", "0", 10], p[2]]]
    elif len(p) == 3:
        p[0] = ["SLICE", p[1], ["PRIMITIVE", ["INT", "-1", 10]]]
    else:
        p[0] = ["SLICE", ["PRIMITIVE", ["INT", "0", 10]], ["PRIMITIVE", ["INT", "-1", 10]]]

def p_indice(p):
    """indice : expr
              | DOTDOTDOT
              |"""

    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None


def p_expr_kernel(p):
    """expr : kernel"""

    p[0] = p[1]

def p_expr_bin_not1(p):
    """expr : expr NOT IN expr %prec NOTIN"""

    p[0] = ["OP", "NOT", ["OP", "IN", p[1], p[4]]]

def p_expr_bin_not2(p):
    """expr : expr ISNT expr"""

    p[0] = ["OP", "NOT", ["OP", "IS", p[1], p[3]]]

def p_expr_un_l1(p):
    """expr : NOT expr"""

    p[0] = ["OP", "NOT", p[2]]

def p_expr_un_l2(p):
    """expr : '-' expr %prec UMINUS
            | '+' expr %prec UMINUS"""

    p[0] = ["OP", "U"+p[1], p[2]]

def p_expr_un_r(p):
    """expr : lvalue PLUSPLUS
            | lvalue MINUSMINUS"""

    p[0] = ["OP", p[2], p[1]]

def p_list_items(p):
    """list_items : list_items ',' expr
                  | expr"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_hash_items(p):
    """hash_items : hash_items ',' expr ':' expr
                  | expr ':' expr"""
    if len(p) == 4:
        p[0] = [(p[1], p[3])]
    else:
        p[0] = p[1]

def p_lvalue_ident(p):
    """lvalue : IDENT"""

    p[0] = ["IDENT", p[1]]

def p_kernel_expr(p):
    """kernel : '(' expr ')'"""

    p[0] = p[2]

def h_loc(p):
    if p[0] == "IDENT":
        return p[1]
    elif p[0] == "OP" and p[1] == "GETINDEX":
        return ["SETINDEX", p[2], p[3]]
    elif p[0] == "GETATTR":
        return ["SETATTR", p[1], p[2]]
    else:
        raise SyntaxError("You're assigning that to WHAT?!")

def p_many_exprs(p):
    """many_exprs : many_exprs ',' expr
                  | expr"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_many_lvalues(p):
    """many_lvalues : many_lvalues ',' lvalue
                    | lvalue"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_many_idents(p):
    """many_idents : many_idents ',' IDENT
                   | IDENT"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_del_s(p):
    """del_s : DEL many_lvalues"""

    p[0] = ["DEL"] + map(h_delloc, p[2])

def h_delloc(p):
    if p[0] == "IDENT":
        return p[1]
    elif p[0] == "OP" and p[1] == "GETINDEX":
        return ["DELINDEX", p[2], p[3]]
    elif p[0] == "GETATTR":
        return ["DELATTR", p[1], p[2]]
    else:
        raise SyntaxError("You're deleting WHAT?!")

def p_extern_s(p):
    """extern_s : EXTERN many_idents"""
    p[0] = ["EXTERN"] + p[2]

def p_flow_s(p):
    """flow_s : BREAK expr
              | BREAK
              | CONTINUE expr
              | CONTINUE
              | THROW expr
              | THROW
              | RETURN many_exprs
              | RETURN many_exprs ','
              | YIELD many_exprs
              | YIELD many_exprs ','"""

    if len(p) == 3:
        p[0] = [p[1].upper(), p[2]]
    else:
        p[0] = [p[1].upper(), None]

def p_import_s(p):
    """import_s : IMPORT import_items
                | IMPORT import_items AS IDENT"""

    if len(p) == 3:
        p[0] = [p[1].upper(), p[2]]
    else:
        if p[2][-1] == "*":
            raise SyntaxError("Can only use 'import ... as ...' with single variable")
        p[0] = [p[1].upper(), p[2], p[4]]

def p_import_items(p):
    """import_items : import_items '.' IDENT
                    | import_items '.' '*'
                    | IDENT"""

    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_assert_s(p):
    """assert_s : ASSERT expr
                | ASSERT expr ',' string"""

    if len(p) == 3:
        p[0] = ["ASSERT", p[2]]
    else:
        p[0] = ["ASSERT", p[2], p[4]]

def p_block_s(p):
    """block_s : if_s
               | while_s
               | for_s
               | try_s"""

    p[0] = p[1]

def p_if_s(p):
    """if_s : if_if if_elifs else"""

    p[0] = p[1] + p[2] + p[3]

def p_if_if(p):
    """if_if : IF expr block"""

    p[0] = ["IF", p[2], p[3]]

def p_if_elif(p):
    """if_elifs : ELIF expr block if_elifs
                | """

    if len(p) == 1:
        p[0] = []
    else:
        p[0] = ["ELIF", p[2], p[3]] + p[4]

def p_else(p):
    """else : ELSE block
            | """

    if len(p) == 1:
        p[0] = []
    else:
        p[0] = ["ELSE", p[2]]

def p_block(p):
    """block : '{' statements '}'"""

    p[0] = p[2]

def p_while_s(p):
    """while_s : WHILE expr block else
               | WHILE block else"""

    if len(p) == 5:
        p[0] = ["WHILE", p[2], p[3]] + p[4]
    else:
        p[0] = ["WHILE", None, p[2]] + p[3]

def p_for_s(p):
    """for_s : FOR many_lvalues IN many_exprs block else"""

    vars = map(h_loc, p[2])

    p[0] = ["FOR", (vars, p[4]), p[5]] + p[6]

def p_try_s(p):
    """try_s : try_try try_catch else try_finally"""

    p[0] = p[1] + p[2] + p[3] + p[4]

def p_try_try(p):
    """try_try : TRY block"""

    p[0] = ["TRY", p[2]]

def p_try_catch(p):
    """try_catch : CATCH many_exprs block try_catch
                 | CATCH many_exprs AS lvalue block try_catch
                 | CATCH block try_catch
                 | """

    if len(p) == 1:
        p[0] = []
    elif len(p) == 5:
        p[0] = ["CATCH", p[2], None, p[3]] + p[4]
    elif len(p) == 7:
        var = h_loc(p[4])
        p[0] = ["CATCH", p[2], var, p[5]] + p[6]
    else:
        p[0] = ["CATCH", [], None, p[2]] + p[3]

def p_try_finally(p):
    """try_finally : FINALLY block
                   | """

    if len(p) == 1:
        p[0] = []
    else:
        p[0] = ["FINALLY", p[2]]

# FUNCTION DEFS
# The EBNF for a function def is
# > fn_s : FN [string] ['(' arg_defs ')'] [IS many_idents] block
# Due to the fact that there is no EBNF in Ply, we're getting 8 different
# rules

def p_fn1(p):
    """fn : FN string '(' arg_defs ')' IS many_idents block"""
    p[0] = [["FN", p[4], p[8], p[2], p[7]]]

def p_fn2(p):
    """fn : FN '(' arg_defs ')' IS many_idents block"""
    p[0] = [["FN", p[3], p[7], "", p[6]]]

def p_fn3(p):
    """fn : FN string '(' arg_defs ')' block"""
    p[0] = [["FN", p[4], p[6], p[2], []]]

def p_fn4(p):
    """fn : FN '(' arg_defs ')' block"""
    p[0] = [["FN", p[3], p[5], "", []]]

def p_fn5(p):
    """fn : FN string IS many_idents block"""
    p[0] = [["FN", [], p[5], p[2], p[4]]]

def p_fn6(p):
    """fn : FN IS many_idents block"""
    p[0] = [["FN", [], p[4], "", p[3]]]

def p_fn7(p):
    """fn : FN string block"""
    p[0] = [["FN", [], p[3], p[2], []]]

def p_fn8(p):
    """fn : FN block"""
    p[0] = [["FN", [], p[2], "", []]]

def p_arg_defs(p):
    """arg_defs : arg_defs ',' arg_def
                | arg_def
                | """

    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_arg_def_expr(p):
    """arg_def_ : IDENT IDENT
                | IDENT"""
    p[0] = ["ARG"] + p[1:]

def p_arg_def_kw(p):
    """arg_def : arg_def_ ASSIGN expr
               | arg_def_"""
    if len(p) == 4:
        p[0] = ["DEFARG"] + p[1][1:] + [p[3]]
    else:
        p[0] = p[1]

def p_arg_def_mult(p):
    """arg_def : '*' IDENT"""
    p[0] = ["UNWRAPABLE", p[2]]

def p_arg_def_kwmult(p):
    """arg_def : '*' '*' IDENT"""
    p[0] = ["UNWRAPABLEKW", p[3]]

# CLASS DEFINITIONS
# The EBNF for a class def is very similar to that of a function def
# class : CLASS [string] ['(' [many_exprs] ')'] [IS many_idents] block

def p_class(p):
    """class : CLASS '(' many_exprs ')' IS many_idents block
             | CLASS '(' ')' IS many_idents block
             | CLASS IS many_idents block
             | CLASS '(' many_exprs ')' block
             | CLASS '(' ')' block
             | CLASS block"""

    if len(p) == 8:
        p[0] = ["CLASS", "", p[3], p[6], p[7]]
    elif len(p) == 7:
        p[0] = ["CLASS", "", [], p[5], p[6]]
    elif len(p) == 5:
        if p[2] == "is":
            p[0] = ["CLASS", "", [], p[3], p[4]]
        else:
            p[0] = ["CLASS", "", [], [], p[4]]
    elif len(p) == 6:
        p[0] = ["CLASS", "", p[3], [], p[5]]
    else:
        p[0] = ["CLASS", "", [], [], p[2]]

def p_class_doc(p):
    """class : CLASS string '(' many_exprs ')' IS many_idents block
             | CLASS string '(' ')' IS many_idents block
             | CLASS string IS many_idents block
             | CLASS string '(' many_exprs ')' block
             | CLASS string '(' ')' block
             | CLASS string block"""

    if len(p) == 9:
        p[0] = ["CLASS", p[2], p[4], p[7], p[8]]
    elif len(p) == 8:
        p[0] = ["CLASS", p[2], [], p[6], p[7]]
    elif len(p) == 6:
        if p[3] == "is":
            p[0] = ["CLASS", p[2], [], p[4], p[5]]
        else:
            p[0] = ["CLASS", p[2], [], [], p[5]]
    elif len(p) == 7:
        p[0] = ["CLASS", p[2], p[4], [], p[6]]
    else:
        p[0] = ["CLASS", p[2], [], [], p[3]]

def p_statement(p):
    """statement : expr
                 | assignment
                 | del_s
                 | extern_s
                 | flow_s
                 | import_s
                 | assert_s
                 | block_s
                 | PROCDIR
                 | PROCBLOCK"""

    txtp = p.lexspan(1)[0]
    while txtp > -1 and parser.txt[txtp] != "\n":
        txtp -= 1

    txtp2 = p.lexspan(1)[1]
    while txtp2 < len(parser.txt) and parser.txt[txtp2] != "\n":
        txtp2 += 1

    code = parser.txt[txtp + 1:txtp2]
    bounds = [txtp, txtp2]
    p[0] = ["STATEMENT", [i+1 for i in p.linespan(1)], bounds, code, p[1]]

def p_statements_aux(p):
    """statements_ : statements_ NEWLINE statement
                   | statement"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_statements2(p):
    """statements : NEWLINE statements_ NEWLINE
                  | NEWLINE statements_"""

    p[0] = p[2]

def p_statements1(p):
    """statements : statements_ NEWLINE
                  | statements_"""

    p[0] = p[1]

def p_statements0(p):
    """statements : NEWLINE
                  | """

    p[0] = []

def p_kernel(p): # MUST go on bottom to resolve r/r conflict correctly
    """kernel : primitive
              | list
              | dict
              | lvalue
              | fn
              | class"""

    p[0] = p[1]

def p_list(p):
    """list : '[' ']'
            | '[' list_items ']'
            | '[' list_items ',' ']'"""
    if len(p) == 3:
        p[0] = ["LIST", []]
    else:
        p[0] = ["LIST", p[2]]

def p_dict(p):
    """dict : '[' hash_items ']'
            | '[' hash_items ',' ']'"""
    p[0] = ["DICT", p[2]]

def p_assignment_single(p):
    """assignment : lvalue EQOP expr
                  | lvalue ASSIGN expr"""

    var = h_loc(p[1])
    p[0] = [p[2], [var], [p[3]]]

def p_assignment_many(p):
    """assignment : lvalue ',' assignment ',' expr"""

    var = h_loc(p[1])
    p[3][1].insert(0, var)
    p[3][2].append(p[5])
    p[0] = p[3]

# There used to be variable type declarations;
# no more. Multiple dispatch can work without
# them. So let's leave oranj as simple as can
# be.

def p_error(t):
    if t:
        e = SyntaxError("(line %d, col %d)" % (t.lineno, getcol(t)) + " The %s confuses me" % repr(t.value).lower())
    else:
        e = SyntaxError("At the end of your input.")

    handle_error(e)

import objects.about
_p = objects.about.mainpath
if not _p.endswith("core"):
    _p += "core/"
parser = yacc.yacc(outputdir=_p+"../build", debug=0)

def parse(s):
    global parser
    parser.errors = 0
    parser.txt = s

    try:
        r = parser.parse(s, tracking=True)
    except (SyntaxError, lex.LexError), e:
        handle_error(e)

    if parser.errors: raise ParseError("Parsing error occurred")
    return r

def handle_error(e):
    global parser
    parser.errors += 1

    print term.render("${RED}%s${NORMAL}" % type(e).__name__ + \
        ("" if not e.args else (": " + " ".join(e.args))))

def getcol(tok):
    global parser

    l = parser.txt.rfind("\n", 0, tok.lexpos)
    if l < 0:
        l = 0
    return (tok.lexpos - l) + 1

def _test():
    import pprint # Because parse trees get hairy

    try:
        while True:
            try:
                pprint.pprint(parse(raw_input("parse> ") + "\n"))
            except ParseError:
                pass
    except (KeyboardInterrupt, EOFError):
        print

if __name__ == "__main__":
    _test()

#!/usr/bin/env python

# A warning to all who wish to edit this module:
# Mostly, what I've done here makes sense
# It might even be what you would do
# But in order to get `a.b, c[0] += 1, 4` to parse...
# I had to sell my soul to the devil
# Careful modifying the rules loc and locs
# Or the loch ness monster will have your soul
#                               -- Pavel


import ply.yacc as yacc
from lexer import tokens, literals
import terminal

class ParseError(Exception): pass

term = terminal.TerminalController()
start = "statements"

def p_primitive(p):
    """primitive : DEC
                 | STRING
                 | INT
                 | NIL
                 | BOOL
                 | INF"""
    p[0] = ["PRIMITIVE", p[1]]

def p_primitive_IDENT(p):
    """ident : IDENT"""
    p[0] = ["IDENT", p[1]]
    
def p_literal_list(p):
    """literal : '[' list_items ']'
               | '[' list_items ',' ']'
               | '[' ']'"""

    if len(p) == 3:
        p[0] = ["LIST", []]
    else:
        p[0] = ["LIST", p[2]]

def p_literal_alist(p):
    """literal : '[' hash_items ']'
               | '[' hash_items ',' ']'"""
    p[0] = ["TABLE", p[2]]

def p_literal_set(p):
    """literal : '{' list_items '}'
               | '{' list_items ',' '}'"""
    p[0] = ["SET", p[2]]

def p_literal_dict(p):
    """literal : '{' hash_items '}'
               | '{' hash_items ',' '}'
               | '{' '}'"""
    if len(p) == 3:
        p[0] = ["DICT", []]
    else:
        p[0] = ["DICT", p[2]]

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
        p[0] = ["OP", "OR", p[1], p[3]]
    else:
        p[0] = p[1]

def p_test_and(p):
    """test_and : test_and AND test_not
                | test_not"""

    if len(p) == 4:
        p[0] = ["OP", "AND", p[1], p[3]]
    else:
        p[0] = p[1]

def p_test_not(p):
    """test_not : NOT test_in
                | test_in"""

    if len(p) == 3:
        p[0] = ["OP", "NOT", p[2]]
    else:
        p[0] = p[1]

def p_test_in(p):
    """test_in : test_in IN test_type
               | test_in NOT IN test_type
               | test_in '|' test_type
               | test_type"""

    if len(p) == 4:
        p[0] = ["OP", p[2], p[1], p[3]]
    elif len(p) == 5:
        p[0] = ["OP", "NOT", ["OP", "IN", p[1], p[4]]]
    else:
        p[0] = p[1]

def p_test_type(p):
    """test_type : test_type IS test_comp
                 | test_type IS NOT test_comp
                 | test_comp"""

    if len(p) == 4:
        p[0] = ["OP", "IS", p[1], p[3]]
    elif len(p) == 5:
        p[0] = ["OP", "NOT", ["OP", "IS", p[1], p[4]]]
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
        p[0] = ["OP", p[2], p[1], p[3]]
    else:
        p[0] = p[1]

def p_test_io(p):
    """test_io : test_io LTLT test_pm
               | test_io GTGT test_pm
               | test_pm"""

    if len(p) == 4:
        p[0] = ["OP", p[2], p[1], p[3]]
    else:
        p[0] = p[1]

def p_test_pm(p):
    """test_pm : test_pm '+' test_mdmf
               | test_pm '-' test_mdmf
               | test_mdmf"""

    if len(p) == 4:
        p[0] = ["OP", p[2], p[1], p[3]]
    else:
        p[0] = p[1]

def p_test_mdmf(p):
    """test_mdmf : test_mdmf '*' test_un
                 | test_mdmf '/' test_un
                 | test_mdmf SLASHSLASH test_un
                 | test_mdmf MOD test_un
                 | test_un"""

    if len(p) > 2:
        p[0] = ["OP", p[2], p[1], p[3]]
    else:
        p[0] = p[1]

def p_test_un(p):
    """test_un : loc PLUSPLUS
               | loc MINUSMINUS
               | '-' test_un
               | '+' test_un
               | test_exp"""

    if len(p) == 3 and p[2] in ("++", "--"):
        p[0] = ["OP", p[2], p[1]]
    elif p[1] in ("+", "-"):
        p[0] = ["OP", "U"+p[1], p[2]]
    else:
        p[0] = p[1]

def p_test_exp(p):
    """test_exp : test_call '^' test_exp
                | test_call"""

    if len(p) == 4:
        p[0] = ["OP", "^", p[1], p[3]]
    else:
        p[0] = p[1]

def p_test_call(p):
    """test_call : test_call_strong
                 | test_attr_strong
                 | test_idx_strong
                 | test_basis"""

    p[0] = p[1]


def p_test_call_strong(p):
    """test_call_strong : test_call '(' arglist ')'
                        | test_call '(' arglist ',' ')'"""
    
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
    """arg : expression"""
    p[0] = p[1]

def p_arg_kw(p):
    """arg : IDENT EQOP expression"""
    if p[2] != "=":
        raise SyntaxError("Dude, what the fuck are you doing?!")
    p[0] = ["KW", p[1], p[3]]

def p_arg_mult(p):
    """arg : '*' expression"""
    p[0] = ["UNWRAP", p[2]]

def p_arg_kwmult(p):
    """arg : '*' '*' expression"""
    p[0] = ["UNWRAPKW", p[3]]

# No, you don't want to know
def p_test_attr_strong(p):
    """test_attr_strong : test_call '.' IDENT"""

    p[0] = ["GETATTR", p[1], p[3]]

def p_test_idx_strong(p):
    """test_idx_strong : test_call '[' index ']'
                       | test_call '[' index ',' ']'
                       | test_call literal
                       | test_basis literal
                       | ident literal"""

    if len(p) == 2 and p[2][0] != "LIST":
        raise SyntaxError("SyntaxError", "WTF are you doing there?!")
    
    if len(p) == 3:
        g = p[2][1]
        if len(g) == 1:
            g = g[0]
        p[0] = ["OP", "GETINDEX", p[1], g]
    else:
        if len(p[3]) == 1:
            p[3] = p[3][0]
        p[0] = ["OP", "GETINDEX", p[1], p[3]]
    
def p_index(p):
    """index : index ',' indice
             | indice"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_indice3(p):
    """indice : expression ':' expression ':' expression
              | ':' expression ':' expression
              | expression ':' ':' expression
              | ':' ':' expression"""
    
    p[0] = ["SLICE", ["PRIMITIVE", ["INT", "0", 10]], ["PRIMITIVE", ["INT", "-1", 10]]]
    if len(p) == 6:
        p[1] = p[1]
        p[2] = p[3]
    elif len(p) == 5 and p[1] == ":":
        p[2] = p[2]
    elif len(p) == 5:
        p[1] = p[1]
    
def p_indice2(p):
    """indice : expression ':' expression
              | ':' expression
              | expression ':'
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
    """indice : expression
              | DOTDOTDOT
              |"""
    
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None

def p_test_basis(p):
    """test_basis : primitive
                  | literal
                  | ident
                  | fn
                  | class"""

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
                 | declaration
                 | PROCDIR
                 | PROCBLOCK
                 | DOTDOTDOT"""
    
    if p[1] == "...":
        p[0] = ["DOTDOTDOT"]
    else:
        p[0] = p[1]

def p_assignment_single(p):
    """assignment : loc EQOP expression"""
    
    t = ["ASSIGN1", p[1], p[3], p[2]]
    
    if p[2] != "=":
        s = p[1][:]
        if type(s) == type(""):
            s = ["IDENT", s]
        elif s[0] == "SETATTR":
            s[0] = "GETATTR"
        elif s[0] == "SETINDEX":
            s[0] = "GETINDEX"
    
        t[2] = ["OP", p[2][:-1], s, p[3]]
    
    p[0] = t

def p_assignment_soul_sold(p):
    """assignment : loc ',' assignment ',' expression"""

    if p[3][0] == "ASSIGN1":
        p[0] = [p[3][3], [p[1], p[3][1]], [p[5], p[3][2]]]
    else:
        p[3][1].insert(0, p[1])
        p[3][2].append(p[5])
        p[0] = p[3]

def p_declaration(p):
    """declaration : ident assignment"""

    p[0] = ["DECLARE", p[1], p[2]]

def p_var_s(p):
    """var_s : DEL locs
             | EXTERN idents"""

    p[0] = [p[1].upper()] + p[2]

def p_idents(p):
    """idents : idents ',' IDENT
              | IDENT"""

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

    p[0] = [p[1].upper(), p[2]]

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
                | IMPORT import_items AS IDENT"""

    if len(p) == 3:
        p[0] = [p[1], p[2]]
    else:
        p[0] = [p[1], p[2], p[4]]

def p_import_items(p):
    """import_items : IDENT '.' import_items
                    | IDENT
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
        p[0] = ["ASSERT", p[2]]
    else:
        p[0] = ["ASSERT", p[2], p[4]]

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

    p[0] = p[1] + p[2] + p[3]

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
    """block : '{' statements '}'
             | literal"""
    
    if len(p) == 4:
        p[0] = p[2]
    else:
        if p[1][0] not in ("DICT", "SET"): raise SyntaxError("That's a " + p[1][0].lower() + ", not a block.")
        p[0] = p[1][1]

def p_while_s(p):
    """while_s : WHILE expression block else
               | WHILE block else"""

    if len(p) == 5:
        p[0] = ["WHILE", p[2], p[3]] + p[4]
    else:
        p[0] = ["WHILE", None, p[2]] + p[3]

def p_for_s(p):
    """for_s : FOR locs IN comma_list block else"""

    p[0] = ["FOR", (p[2], p[4]), p[5]] + p[6]

def p_try_s(p):
    """try_s : try_try try_catch else"""

    p[0] = p[1] + p[2] + p[3]

def p_try_try(p):
    """try_try : TRY block"""

    p[0] = ["TRY", p[2]]

def p_try_catch(p):
    """try_catch : CATCH comma_list block try_catch
                 | CATCH comma_list AS ident block try_catch
                 | CATCH block try_catch
                 | """

    if len(p) == 1:
        p[0] = []
    elif len(p) == 5:
        p[0] = ["CATCH", p[2], None, p[3]] + p[4]
    elif len(p) == 7:
        p[0] = ["CATCH", p[2], p[4], p[5]] + p[6]
    else:
        p[0] = ["CATCH", [], None, p[2]] + p[3]

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

def p_rettype(p):
    """rettype : IDENT
               | NIL"""
    
    p[0] = p[1] if p[1] != None else "nil"

def p_fn1(p):
    """fn : FN STRING '(' arg_defs ')' rettype block"""
    p[0] = [["FN", p[4], p[7], p[2][1], p[6]]]

def p_fn2(p):
    """fn : FN '(' arg_defs ')' rettype block"""
    p[0] = [["FN", p[3], p[6], "", p[5]]]

def p_fn3(p):
    """fn : FN STRING '(' arg_defs ')' block"""
    p[0] = [["FN", p[4], p[6], p[2][1], ""]]

def p_fn4(p):
    """fn : FN '(' arg_defs ')' block"""
    p[0] = [["FN", p[3], p[5], "", ""]]

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

def p_class(p):
    """class : CLASS '(' comma_list ')' IS idents block
             | CLASS '(' ')' IS idents block
             | CLASS IS idents block
             | CLASS '(' comma_list ')' block
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
    """class : CLASS STRING '(' comma_list ')' IS idents block
             | CLASS STRING '(' ')' IS idents block
             | CLASS STRING IS idents block
             | CLASS STRING '(' comma_list ')' block
             | CLASS STRING '(' ')' block
             | CLASS STRING block"""

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

def p_arg_def_expr(p):
    """arg_def : expression
               | IDENT expression"""
    p[0] = ["ARG"] + p[1:]

def p_arg_def_kw(p):
    """arg_def : IDENT '=' expression
               | IDENT IDENT '=' expression"""
    p[0] = ["ARG"] + p[1:]

def p_arg_def_mult(p):
    """arg_def : '*' IDENT"""
    p[0] = ["UNWRAPABLE", p[2]]

def p_arg_def_kwmult(p):
    """arg_def : '*' '*' IDENT"""
    p[0] = ["UNWRAPABLEKW", p[3]]

# I've heard that making this here might fix things
def p_loc(p):
    """loc : ident
           | test_attr_strong
           | test_idx_strong"""

    if p[1][0] == "IDENT":
        p[0] = p[1][1]
    elif p[1][0] == "OP" and p[1][1] == "GETINDEX":
        p[0] = ["SETINDEX", p[1][2], p[1][3]]
    elif p[1][0] == "GETATTR":
        p[0] = ["SETATTR", p[1][1], p[1][2]]
    else:
        raise SyntaxError("SyntaxError", "You're assigning that to WHAT?!")

def p_locs(p):
    """locs : locs ',' loc
            | loc"""

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

    
def p_error(t):
    try:
        e = Exception("SyntaxError (line %d, col %d)" % (t.lineno, getcol(t)), "The %s confuses me" % repr(t.value).lower())
    except:
        raise
        e = Exception("SyntaxError", "No idea where though.")
    
    handle_error(e)

yacc.yacc()

def getcol(tok):
    l = in_put.rfind("\n", 0, tok.lexpos)
    if l < 0:
        l = 0
    return (tok.lexpos - l) + 1

def parse(s):
    global errors
    errors = 0
    global in_put
    in_put = s
    
    try:
        r = yacc.parse(s)
    except SyntaxError, e:
        handle_error(e)
    
    if errors: raise ParseError("Parsing error occurred")
    return r

def handle_error(e):
    global errors
    print term.render("${RED}%s${NORMAL}" % e.args[0] + ("" if len(e.args) == 1 else (": " + " ".join(e.args[1:]))))
    errors += 1

def _test(s):
    global errors
    y = parse(s)
    
    if type(y) == type([]) and len(y) > 1:
        errors += 1

    if not errors:
        pprint.pprint(y[0])

if __name__ == "__main__":
    import pprint # Because parse trees get hairy
    import sys
    
    if len(sys.argv) == 2:
        y = parse(open(sys.argv[1]).read())
    else:
        while True:
            try:
                _test(raw_input("parse> ") + "\n")
            except (EOFError, KeyboardInterrupt):
                break
            except ParseError:
                continue

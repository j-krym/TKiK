from __future__ import annotations

from lark import Lark

from transformer import CToASTTransformer

GRAMMAR = r"""
    ?start: program

    program: item*

    ?item: function_def
         | struct_def ";"
         | declaration ";"
         | comment
         | include_stmt

    INCLUDE: "#include"
    HEADER: /<[^>]+>/     
    include_stmt: INCLUDE HEADER

    struct_def: "struct" IDENT "{" struct_field* "}"
    struct_field: type_spec IDENT ";"

    function_def: type_spec IDENT "(" param_list? ")" block

    param_list: param ("," param)*
    array_suffix: "[" "]"

    param: type_spec IDENT array_suffix?

    block: "{" statement* "}"

    ?statement: declaration ";"
              | assignment ";"
              | inc_dec_stmt ";"
              | if_stmt
              | while_stmt
              | for_stmt
              | switch_stmt
              | return_stmt ";"
              | expr_stmt ";"
              | break_stmt
              | continue_stmt
              | block
              | ";"
              | comment

    break_stmt: "break" ";"
    continue_stmt: "continue" ";"

    if_stmt:     "if" "(" condition ")" statement else_clause?
    else_clause: "else" statement

    while_stmt: "while" "(" condition ")" statement

    for_stmt: "for" "(" for_init? ";" condition? ";" for_post? ")" statement
    for_init: declaration
            | assignment
            | expr
    for_post: assignment
            | inc_dec_stmt
            | expr

    inc_dec_stmt: IDENT INC -> post_inc_stmt
                | IDENT DEC -> post_dec_stmt
                | INC IDENT -> pre_inc_stmt
                | DEC IDENT -> pre_dec_stmt

    switch_stmt: "switch" "(" expr ")" "{" case_block* default_block? "}"
    case_block: "case" expr ":" statement* break_stmt
    default_block: "default" ":" statement*

    declaration: type_spec decl ("," decl)*
    decl: IDENT array_size? ("=" expr)?
    array_size: "[" expr "]" -> array_size

    assignment: lvalue ASSIGN_OP expr
    ?lvalue: IDENT suffix*
    ASSIGN_OP: "=" | "+=" | "-=" | "*=" | "/="

    return_stmt: "return" expr?
    expr_stmt: expr

    ?condition: expr

    ?expr: ternary

    ?ternary: logic_or ("?" ternary ":" ternary)?

    ?logic_or:  logic_and (OR_OP logic_and)*
    ?logic_and: comparison (AND_OP comparison)*

    ?comparison: sum (COMP_OP sum)?
    COMP_OP: "==" | "!=" | "<=" | ">=" | "<" | ">"
    AND_OP: "&&"
    OR_OP: "||"
    PLUS: "+"
    MINUS: "-"
    MUL: "*"
    DIV: "/"
    MOD: "%"

    INC: "++"
    DEC: "--"

    ?sum:  term ((PLUS | MINUS) term)*
    ?term: factor ((MUL | DIV | MOD) factor)*

    ?factor: "!" factor      -> log_not
           | postfix

    ?postfix: primary suffix*
    suffix: "." IDENT        -> member_suffix
          | "[" expr "]"     -> index_suffix

    ?primary: call
            | NUMBER       -> number
            | STRING       -> string
            | IDENT        -> var
            | BOOLEAN      -> bool
            | list_literal
            | "(" expr ")"
            | MINUS factor -> neg
            | PLUS factor  -> pos

    list_literal: "[" (expr ("," expr)*)? "]"

    call: IDENT "(" arg_list? ")"
    arg_list: expr ("," expr)*

    ?type_spec: (INT_TYPE | FLOAT_TYPE | struct_type) ("[" "]")* | VOID_TYPE
    INT_TYPE:   "int"
    FLOAT_TYPE: "float"
    VOID_TYPE: "void"
    struct_type: "struct" IDENT

    BOOLEAN: "true" | "false"
    IDENT:   /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER:  /[0-9]+(?:\.[0-9]+)?/
    STRING:  /"(?:[^"\\]|\\.)*"/

    comment: CPP_COMMENT | C_COMMENT
    CPP_COMMENT: /\/\/[^\n]*/
    C_COMMENT:   /\/\*[\s\S]*?\*\//

    %import common.WS
    %ignore WS
"""


class CParser:
    def __init__(self) -> None:
        self._lark = Lark(
            GRAMMAR,
            parser="lalr",
            start="start",
            propagate_positions=False,
            maybe_placeholders=True,
        )
        self._transformer = CToASTTransformer()

    def parse(self, source: str):
        tree = self._lark.parse(source)
        return self._transformer.transform(tree)

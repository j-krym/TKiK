
### Translator języka C do Python

- Jacek Krymer jkrymer@student.agh.edu.pl
- Jakub Knapik jakubknapik@student.agh.edu.pl

## Założenia programu

**Ogólne cele programu:**  
Stworzenie narzędzia automatycznie tłumaczącego kod języka C na równoważny kod w języku Python.

**Rodzaj translatora:**  
Kompilator (transpiler, source-to-source).

**Planowany wynik działania programu:**  
Kod źródłowy w Pythonie wygenerowany na podstawie wejściowego programu w C.

**Planowany język implementacji:**  
Python

**Sposób realizacji skanera/parsera:**  
Wykorzystanie generatora parserów LARK

## Opis tokenów

| Token Name  | Pattern / Value             | Description                                                        |
| ----------- | --------------------------- | ------------------------------------------------------------------ |
| INT_TYPE    | `int`                       | Integer data type keyword.                                         |
| FLOAT_TYPE  | `float`                     | Floating-point data type keyword.                                  |
| STRUCT      | `struct`                    | Keyword for struct type
| IF          | `if`                        | Initiates a conditional statement block.                           |
| ELSE        | `else`                      | Defines the alternative branch of a conditional statement.         |
| WHILE       | `while`                     | Keyword for while loop.                                            |
| FOR         | `for`                       | Keyword for for loop.                                              |
| SWITCH      | `switch`                    | Switch-case control flow keyword.                                  |
| CASE        | `case`                      | Defines a branch in a switch statement.                            |
| DEFAULT     | `default`                   | Default branch in a switch statement.                              |
| RETURN      | `return`                    | Function return statement keyword.                                 |
| BREAK       | `break`                     | Loop or switch break statement keyword.                            |
| CONTINUE    | `continue`                  | Loop continue statement keyword.                                   |
| BOOLEAN     | `true` \| `false`            | Boolean literals.                                                  |
| IDENT       | `[a-zA-Z_][a-zA-Z0-9_]*`    | User-defined identifiers for variables, functions, and parameters. |
| NUMBER      | `[0-9]+(?:\.[0-9]+)?`       | Numeric literals (integers and floating-point numbers).            |
| STRING      | `"(?:[^"\\]\|\\.)*"`        | String literals with escape sequence support.                      |
| PLUS        | `+`                         | Arithmetic addition operator or unary plus.                        |
| MINUS       | `-`                         | Arithmetic subtraction operator or unary negation.                 |
| MUL         | `*`                         | Arithmetic multiplication operator.                                |
| DIV         | `/`                         | Arithmetic division operator.                                      |
| MOD         | `%`                         | Modulo (remainder) operator.                                       |
| INC         | `++`                        | Increment operator (prefix or postfix).                            |
| DEC         | `--`                        | Decrement operator (prefix or postfix).                            |
| COMP_OP     | `==` `!=` `<` `>` `<=` `>=` | Comparison operators.                                              |
| AND         | `&&`                        | Logical conjunction (AND) operator.                                |
| OR          | `\|\|`                      | Logical disjunction (OR) operator.                                 |
| NOT         | `!`                         | Logical negation (NOT) operator.                                   |
| ASSIGN_OP   | `=` `+=` `-=` `*=` `/=`     | Assignment operators.                                              |
| QUESTION    | `?`                         | Ternary conditional operator (first part).                         |
| COLON       | `:`                         | Used in ternary operator and switch-case labels.                   |
| DOT         | `.`                         | Struct member access
| LPAREN      | `(`                         | Left parenthesis - grouping and function calls.                    |
| RPAREN      | `)`                         | Right parenthesis - grouping and function calls.                   |
| LBRACE      | `{`                         | Left brace - block delimiter.                                      |
| RBRACE      | `}`                         | Right brace - block delimiter.                                     |
| LBRACKET    | `[`                         | Left square bracket - array indexing.                              |
| RBRACKET    | `]`                         | Right square bracket - array indexing.                             |
| COMMA       | `,`                         | Parameter and argument separator.                                  |
| SEMICOLON   | `;`                         | Statement terminator.                                              |
| CPP_COMMENT | `//[^\n]*`                  | Single-line comment (preserved in AST).                            |
| C_COMMENT   | `/\*[\s\S]*?\*/`            | Multi-line comment (preserved in AST).                             |
| WS          | `[ \t\f\r\n]+`              | Whitespace characters (ignored by lexer).                          |


## Gramatyka


        ?start: program

        program: item*

        ?item: function_def
        | struct_def
        | declaration ";"
        | comment

        struct_def: "struct" IDENT "{" struct_field* "}"
        struct_field: type_spec IDENT ";"

        function_def: type_spec IDENT "(" param_list? ")" block

        param_list: param ("," param)*
        param: type_spec IDENT

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
                | "break" ";"      -> break_stmt
                | "continue" ";"   -> continue_stmt
                | block
                | ";"
                | comment

        if_stmt:     "if" "(" condition ")" statement elif_clause* else_clause?
        elif_clause: "else" "if" "(" condition ")" statement
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
        case_block: "case" expr ":" statement* "break" ";"
        default_block: "default" ":" statement*

        declaration: type_spec decl ("," decl)*
        decl: IDENT ("=" expr)?

        assignment: lvalue ASSIGN_OP expr
        ?lvalue: IDENT          -> var_ref
        | index_access   -> index_ref
        | member_access  -> member_ref
        ASSIGN_OP: "=" | "+=" | "-=" | "*=" | "/="

        return_stmt: "return" expr?
        expr_stmt: expr

        ?condition: expr

        ?expr: ternary

        ?ternary: logic_or ("?" ternary ":" ternary)?

        ?logic_or:  logic_and ("||" logic_and)*
        ?logic_and: comparison ("&&" comparison)*

        ?comparison: sum (COMP_OP sum)?
        COMP_OP: "==" | "!=" | "<=" | ">=" | "<" | ">"

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
        | call
        | member_access
        | index_access
        | atom

        member_access: (IDENT | call | index_access) ("." IDENT)+

        index_access: (IDENT | call) ("[" expr "]")*

        ?atom: NUMBER       -> number
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

        ?type_spec: (INT_TYPE | FLOAT_TYPE | struct_type) ("[" "]")*
        INT_TYPE:   "int"
        FLOAT_TYPE: "float"
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

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
Wykorzystanie generatora parserów ANTLR

## Opis tokenów

| Token Name | Pattern / Value | Description |
|-----------|-----------------|-------------|
| INT_TYPE | `int` | Integer data type keyword. |
| FLOAT_TYPE | `float` | Floating-point data type keyword. |
| IF | `if` | Initiates a conditional statement block. |
| ELSE | `else` | Defines the alternative branch of a conditional statement. |
| WHILE | `while` | Keyword for while loop. |
| FOR | `for` | Keyword for for loop. |
| RETURN | `return` | Function return statement keyword. |
| BREAK | `break` | Loop break statement keyword. |
| CONTINUE | `continue` | Loop continue statement keyword. |
| BOOLEAN | `true` \| `false` | Boolean literals. |
| IDENT | `[a-zA-Z_][a-zA-Z0-9_]*` | User-defined identifiers for variables, functions, and parameters. |
| NUMBER | `[0-9]+(?:\.[0-9]+)?` | Numeric literals (integers and floating-point numbers). |
| STRING | `"(?:[^"\\]|\\.)*"` | String literals enclosed in double quotes. |
| PLUS | `+` | Arithmetic addition operator or unary plus. |
| MINUS | `-` | Arithmetic subtraction operator or unary negation. |
| MUL | `*` | Arithmetic multiplication operator. |
| DIV | `/` | Arithmetic division operator. |
| MOD | `%` | Modulo (remainder) operator. |
| EQ | `==` | Relational equality operator. |
| NE | `!=` | Relational inequality operator. |
| LT | `<` | Relational less-than operator. |
| GT | `>` | Relational greater-than operator. |
| LE | `<=` | Relational less-than-or-equal operator. |
| GE | `>=` | Relational greater-than-or-equal operator. |
| AND | `&&` | Logical conjunction (AND) operator. |
| OR | `\|\|` | Logical disjunction (OR) operator. |
| NOT | `!` | Logical negation (NOT) operator. |
| ASSIGN | `=` | Assignment operator. |
| PLUS_ASSIGN | `+=` | Addition assignment operator. |
| MINUS_ASSIGN | `-=` | Subtraction assignment operator. |
| MUL_ASSIGN | `*=` | Multiplication assignment operator. |
| DIV_ASSIGN | `/=` | Division assignment operator. |
| QUESTION | `?` | Ternary conditional operator (first part). |
| COLON | `:` | Ternary conditional operator (second part) or statement separator. |
| LPAREN | `(` | Left parenthesis - syntactic delimiter. |
| RPAREN | `)` | Right parenthesis - syntactic delimiter. |
| LBRACE | `{` | Left brace - block delimiter. |
| RBRACE | `}` | Right brace - block delimiter. |
| LBRACKET | `[` | Left square bracket - array index delimiter. |
| RBRACKET | `]` | Right square bracket - array index delimiter. |
| COMMA | `,` | Parameter/argument separator. |
| SEMICOLON | `;` | Statement terminator. |
| CPP_COMMENT | `//[^\n]*` | C++-style single-line comment (ignored). |
| C_COMMENT | `/\*[\s\S]*?\*/` | C-style multi-line comment (ignored). |
| WS | `[ \t\f\r\n]+` | Whitespace characters (ignored). |

## Gramatyka


    ?start: program

    program: item*

    ?item: function_def
         | declaration ";"

    function_def: type_spec IDENT "(" param_list? ")" block

    param_list: param ("," param)*
    param: type_spec IDENT

    block: "{" statement* "}"

    ?statement: declaration ";"
              | assignment ";"
              | if_stmt
              | while_stmt
              | for_stmt
              | return_stmt ";"
              | expr_stmt ";"
              | "break" ";"      -> break_stmt
              | "continue" ";"   -> continue_stmt
              | block
              | ";"

    if_stmt: "if" "(" expr ")" statement elif_clause* else_clause?
    elif_clause: "else" "if" "(" expr ")" statement
    else_clause: "else" statement
    
    while_stmt: "while" "(" expr ")" statement
    
    for_stmt: "for" "(" for_init? ";" expr? ";" for_post? ")" statement
    for_init: declaration_nosemi
            | assignment
            | expr
    for_post: assignment
            | expr

    declaration: type_spec decl ("," decl)*
    decl: IDENT ("=" expr)?

    declaration_nosemi: type_spec IDENT ("=" expr)?

    assignment: lvalue ASSIGN_OP expr
    ?lvalue: IDENT           -> var_ref
           | index_access    -> index_ref
    ASSIGN_OP: "=" | "+=" | "-=" | "*=" | "/="


    return_stmt: "return" expr?
    expr_stmt: expr

    ?expr: ternary

    ?ternary: logic_or ("?" expr ":" expr)?

    ?logic_or: logic_and ("||" logic_and)*
    ?logic_and: comparison ("&&" comparison)*

    ?comparison: sum (COMP_OP sum)?
    COMP_OP: "==" | "!=" | "<=" | ">=" | "<" | ">"

    PLUS: "+"
    MINUS: "-"
    MUL: "*"
    DIV: "/"
    MOD: "%"

    ?sum: term ((PLUS | MINUS) term)*
    ?term: factor ((MUL | DIV | MOD) factor)*

    ?factor: "!" factor      -> log_not
           | call
           | index_access
           | atom

    index_access: (IDENT | call) ("[" expr "]")*

    ?atom: NUMBER   -> number
         | STRING   -> string
         | IDENT    -> var
         | BOOLEAN  -> bool
         | list_literal
         | "(" expr ")"
         | MINUS factor -> neg
         | PLUS factor  -> pos

    list_literal: "[" (expr ("," expr)*)? "]"

    call: IDENT "(" arg_list? ")"
    arg_list: expr ("," expr)*
    
    ?type_spec: (INT_TYPE | FLOAT_TYPE) ("[" "]")*
    INT_TYPE: "int"
    FLOAT_TYPE: "float"
    
    BOOLEAN: "true" | "false"
    IDENT: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /[0-9]+(?:\.[0-9]+)?/
    STRING: /"(?:[^"\\]|\\.)*"/

    CPP_COMMENT: /\/\/[^\n]*/
    C_COMMENT: /\/\*[\s\S]*?\*\//

    %import common.WS
    %ignore WS
    %ignore CPP_COMMENT
    %ignore C_COMMENT

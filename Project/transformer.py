from __future__ import annotations

from typing import Any, Iterable, List, Optional

from lark import Token, Transformer

from utils import (
    Assignment,
    BinaryOp,
    Block,
    Boolean,
    BreakStmt,
    Call,
    CaseBlock,
    ContinueStmt,
    DefaultBlock,
    Empty,
    Expr,
    ExprStmt,
    For,
    FunctionDef,
    If,
    IncDecStmt,
    IndexAccess,
    ListLiteral,
    MemberAccess,
    Number,
    Param,
    Program,
    Return,
    Statement,
    String,
    StructDef,
    StructField,
    SwitchStmt,
    TernaryOp,
    UnaryOp,
    Var,
    VarDecl,
    While,
)


def _flatten_statements(values: Iterable[Any]) -> list[Statement]:
    out: list[Statement] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, list):
            out.extend(_flatten_statements(value))
        elif isinstance(value, Block):
            out.extend(_flatten_statements(value.body))
        elif isinstance(value, Statement):
            if not isinstance(value, Empty):
                out.append(value)
        else:
            raise TypeError(f"expected statement-like value, got {type(value)!r}")
    return out


class CToASTTransformer(Transformer):
    def program(self, children):
        items = []
        for child in children:
            if child is None:
                continue
            if isinstance(child, list):
                items.extend(child)
            else:
                items.append(child)
        return Program(items=items)

    def include_stmt(self, children):
        return None

    def struct_def(self, children):
        name = children[0]
        fields = children[1:] if len(children) > 1 else []
        return StructDef(name=name, fields=fields)

    def struct_field(self, children):
        return StructField(type=children[0], name=children[1])

    def function_def(self, children):
        return_type, name, *rest = children
        params: list[Param]
        body_value: Any
        if len(rest) == 1:
            params = []
            body_value = rest[0]
        else:
            params = rest[0]
            body_value = rest[1]
        body = _flatten_statements(body_value if isinstance(body_value, list) else [body_value])
        return FunctionDef(return_type=return_type, name=name, params=params, body=body)

    def param_list(self, children):
        return list(children)

    def param(self, children):
        return Param(type=children[0], name=children[1])

    def array_suffix(self, children):
        return "[]"

    def block(self, children):
        return _flatten_statements(children)

    def declaration(self, children):
        decl_type, *decls = children
        vars: list[VarDecl] = []
        for decl in decls:
            _, name, array_size, init = decl

            vars.append(
                VarDecl(
                    type=decl_type,
                    name=name,
                    init=init,
                    array_size=array_size
                )
            )
        return vars if len(vars) != 1 else vars[0]

    def decl(self, children):
        name = children[0]

        array_size = None
        init = None

        for child in children[1:]:
            if isinstance(child, tuple) and child[0] == "array_size":
                array_size = child[1]
            else:
                init = child

        return ("decl", name, array_size, init)

    def array_decl(self, children):
        print("ARRAY DECL:", children)
        name = children[0]
        size = children[1]
        return ("array", name, size)

    def array_size(self, children):
        return ("array_size", children[0])

    def assignment(self, children):
        target, op, value = children
        return Assignment(target=target, op=str(op), value=value)

    def lvalue(self, children):
        base = Var(name=children[0])
        for suffix in children[1:]:
            if suffix[0] == "member":
                base = MemberAccess(base=base, member=suffix[1])
            elif suffix[0] == "index":
                base = IndexAccess(base=base, index=suffix[1])
            else:
                raise ValueError(f"unsupported lvalue suffix: {suffix!r}")
        return base

    def return_stmt(self, children):
        return Return(value=children[0] if children else None)

    def expr_stmt(self, children):
        return ExprStmt(expr=children[0])

    def comment(self, children):
        return Empty()

    def if_stmt(self, children):
        condition = children[0]
        then_part = children[1]
        then_body = _flatten_statements(then_part if isinstance(then_part, list) else [then_part])
        else_body = None
        if len(children) > 2 and children[2] is not None:
            else_body = children[2]
        return If(condition=condition, then_body=then_body, else_body=else_body)

    def elif_clause(self, children):
        condition = children[0]
        stmt = children[1]
        body = _flatten_statements(stmt if isinstance(stmt, list) else [stmt])
        return ("elif", condition, body)

    def else_clause(self, children):
        stmt = children[0]
        return _flatten_statements(stmt if isinstance(stmt, list) else [stmt])

    def while_stmt(self, children):
        condition = children[0]
        body_part = children[1]
        body = _flatten_statements(body_part if isinstance(body_part, list) else [body_part])
        return While(condition=condition, body=body)

    def for_stmt(self, children):
        if len(children) != 4:
            raise ValueError(f"unexpected for-statement children: {children!r}")
        init, condition, post, body = children

        if init is not None and isinstance(init, Expr):
            init = ExprStmt(init)
        if post is not None and isinstance(post, Expr):
            post = ExprStmt(post)
        body_list = _flatten_statements(body if isinstance(body, list) else [body])
        return For(init=init, condition=condition, post=post, body=body_list)

    def switch_stmt(self, children):
        expr = children[0]
        cases: list[CaseBlock] = []
        default: Optional[DefaultBlock] = None
        for child in children[1:]:
            if isinstance(child, CaseBlock):
                cases.append(child)
            elif isinstance(child, DefaultBlock):
                default = child
            elif child is None:
                continue
            else:
                raise TypeError(f"unsupported switch child: {child!r}")
        return SwitchStmt(expr=expr, cases=cases, default=default)

    def case_block(self, children):
        value = children[0]
        body_children = children[1:]
        if body_children and isinstance(body_children[-1], BreakStmt):
            body_children = body_children[:-1]
        body = _flatten_statements(body_children)
        return CaseBlock(value=value, body=body)

    def default_block(self, children):
        body = _flatten_statements(children)
        return DefaultBlock(body=body)

    def post_inc_stmt(self, children):
        return IncDecStmt(var=children[0], op="++", is_prefix=False)

    def post_dec_stmt(self, children):
        return IncDecStmt(var=children[0], op="--", is_prefix=False)

    def pre_inc_stmt(self, children):
        return IncDecStmt(var=children[0], op="++", is_prefix=True)

    def pre_dec_stmt(self, children):
        return IncDecStmt(var=children[0], op="--", is_prefix=True)

    def call(self, children):
        name = children[0]
        args = children[1] if len(children) > 1 else []
        return Call(func=name, args=args)

    def arg_list(self, children):
        return list(children)

    def postfix(self, children):
        base = children[0]
        for suffix in children[1:]:
            if suffix[0] == "member":
                base = MemberAccess(base=base, member=suffix[1])
            elif suffix[0] == "index":
                base = IndexAccess(base=base, index=suffix[1])
            else:
                raise ValueError(f"unsupported postfix suffix: {suffix!r}")
        return base

    def member_suffix(self, children):
        return ("member", children[0])

    def index_suffix(self, children):
        return ("index", children[0])

    def comparison(self, children):
        if len(children) == 1:
            return children[0]
        left, op, right = children
        return BinaryOp(left=left, op=str(op), right=right)

    def sum(self, children):
        return self._fold_left(children)

    def term(self, children):
        return self._fold_left(children)

    def _fold_left(self, children):
        if len(children) == 1:
            return children[0]
        node = children[0]
        for i in range(1, len(children), 2):
            op = str(children[i])
            rhs = children[i + 1]
            node = BinaryOp(left=node, op=op, right=rhs)
        return node

    def neg(self, children):
        return UnaryOp(op="-", operand=children[0])

    def pos(self, children):
        return children[0]

    def number(self, children):
        text = str(children[0])
        if "." in text:
            return Number(value=float(text))
        return Number(value=int(text))

    def string(self, children):
        token = str(children[0])
        content = token[1:-1]
        value = bytes(content, "utf-8").decode("unicode_escape")
        return String(value=value)

    def var(self, children):
        return Var(name=str(children[0]))

    def type_spec(self, children):
        if not children:
            return ""
        base_type = str(children[0])
        array_suffix = "".join("[]" for _ in children[1:])
        return base_type + array_suffix

    def struct_type(self, children):
        if not children:
            return ""
        return f"struct {children[0]}"

    def INT_TYPE(self, token):
        return str(token)

    def FLOAT_TYPE(self, token):
        return str(token)

    def VOID_TYPE(self, token):
        return str(token)

    def IDENT(self, token):
        return str(token)

    def NUMBER(self, token):
        return str(token)

    def STRING(self, token):
        return str(token)

    def COMP_OP(self, token):
        return str(token)

    def PLUS(self, token):
        return str(token)

    def MINUS(self, token):
        return str(token)

    def MUL(self, token):
        return str(token)

    def DIV(self, token):
        return str(token)

    def __default_token__(self, token):
        return str(token)

    def list_literal(self, children):
        return ListLiteral(elements=children if children else [])

    def bool(self, children):
        return Boolean(value=children[0] == "true")

    def ternary(self, children):
        if len(children) == 1:
            return children[0]
        condition, then_expr, else_expr = children[0], children[1], children[2]
        return TernaryOp(condition=condition, then_expr=then_expr, else_expr=else_expr)

    def logic_or(self, children):
        return self._fold_left_logic(children)

    def logic_and(self, children):
        return self._fold_left_logic(children)

    def log_not(self, children):
        return UnaryOp(op="not", operand=children[0])

    def _fold_left_logic(self, children):
        if len(children) == 1:
            return children[0]
        node = children[0]
        for i in range(1, len(children), 2):
            op = str(children[i])
            rhs = children[i + 1]
            node = BinaryOp(left=node, op=op, right=rhs)
        return node

    def __default__(self, data, children, meta):
        if len(children) == 1:
            return children[0]
        return children

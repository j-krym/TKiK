from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Sequence


class ASTNode:
    """Base class for all AST nodes."""


class Statement(ASTNode):
    pass


class Expr(ASTNode):
    pass


@dataclass
class Program(ASTNode):
    items: List[ASTNode] = field(default_factory=list)


@dataclass
class Param(ASTNode):
    type: str
    name: str


@dataclass
class FunctionDef(ASTNode):
    return_type: str
    name: str
    params: List[Param]
    body: List[Statement]


@dataclass
class VarDecl(Statement):
    type: str
    name: str
    init: Optional[Expr] = None
    array_size: Optional[Expr] = None


@dataclass
class Assignment(Statement):
    target: Expr  # Changed from str to Expr to support lvalue expressions
    op: str
    value: Expr


@dataclass
class ExprStmt(Statement):
    expr: Expr


@dataclass
class If(Statement):
    condition: Expr
    then_body: List[Statement]
    else_body: Optional[List[Statement]] = None


@dataclass
class While(Statement):
    condition: Expr
    body: List[Statement]


@dataclass
class For(Statement):
    init: Optional[Statement]
    condition: Optional[Expr]
    post: Optional[Statement]
    body: List[Statement]


@dataclass
class Return(Statement):
    value: Optional[Expr] = None


@dataclass
class Block(Statement):
    body: List[Statement]


@dataclass
class BinaryOp(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr


@dataclass
class Number(Expr):
    value: int | float


@dataclass
class String(Expr):
    value: str


@dataclass
class Var(Expr):
    name: str


@dataclass
class Call(Expr):
    func: str
    args: List[Expr]


@dataclass
class StructDef(ASTNode):
    name: str
    fields: List[StructField] = field(default_factory=list)


@dataclass
class StructField(ASTNode):
    type: str
    name: str


@dataclass
class IncDecStmt(Statement):
    var: str
    op: str  # "++" or "--"
    is_prefix: bool


@dataclass
class SwitchStmt(Statement):
    expr: Expr
    cases: List[CaseBlock]
    default: Optional[DefaultBlock] = None


@dataclass
class CaseBlock(ASTNode):
    value: Expr
    body: List[Statement]


@dataclass
class DefaultBlock(ASTNode):
    body: List[Statement]


@dataclass
class BreakStmt(Statement):
    pass


@dataclass
class ContinueStmt(Statement):
    pass


@dataclass
class MemberAccess(Expr):
    base: Expr
    member: str


@dataclass
class IndexAccess(Expr):
    base: Expr
    index: Expr


@dataclass
class ListLiteral(Expr):
    elements: List[Expr] = field(default_factory=list)


@dataclass
class TernaryOp(Expr):
    condition: Expr
    then_expr: Expr
    else_expr: Expr


@dataclass
class Boolean(Expr):
    value: bool


@dataclass
class MemberAccess(Expr):
    base: Expr
    member: str


@dataclass
class Empty(Statement):
    pass


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

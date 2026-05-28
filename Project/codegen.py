from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

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
    Program,
    Return,
    Statement,
    String,
    StructDef,
    SwitchStmt,
    TernaryOp,
    UnaryOp,
    Var,
    VarDecl,
    While,
)


@dataclass
class Rendered:
    text: str
    precedence: int


class CodeGenerator:
    def __init__(self, indent: str = "    ") -> None:
        self.indent = indent

    def generate(self, program: Program) -> str:
        lines: list[str] = []
        for index, item in enumerate(program.items):
            rendered = self._render_item(item)
            if rendered:
                lines.extend(rendered)
                if index != len(program.items) - 1:
                    lines.append("")
        output = "\n".join(lines).rstrip()

        if any(
            isinstance(item, FunctionDef) and item.name == "main"
            for item in program.items
        ):
            output += '\n\nif __name__ == "__main__":\n'
            output += '    main()\n'

        return output

    def _render_item(self, item) -> list[str]:
        if isinstance(item, FunctionDef):
            return self._render_function(item)
        if isinstance(item, StructDef):
            return self._render_struct(item)
        if isinstance(item, VarDecl):
            return self._render_vardecl(item, 0)
        if isinstance(item, Statement):
            return self._render_statement(item, 0)
        raise TypeError(f"unsupported top-level node: {type(item)!r}")

    def _render_function(self, node: FunctionDef) -> list[str]:
        params = ", ".join(param.name for param in node.params)
        lines = [f"def {node.name}({params}):"]
        body_lines = self._render_statements(node.body, 1)
        if not body_lines:
            body_lines = [self._indent_line("pass", 1)]
        lines.extend(body_lines)
        return lines

    def _render_statements(self, statements: list[Statement], level: int) -> list[str]:
        lines: list[str] = []
        for stmt in statements:
            lines.extend(self._render_statement(stmt, level))
        return lines

    def _render_statement(self, stmt: Statement, level: int) -> list[str]:
        if isinstance(stmt, Block):
            return self._render_statements(stmt.body, level)
        if isinstance(stmt, VarDecl):
            return self._render_vardecl(stmt, level)
        if isinstance(stmt, Assignment):
            target = self._render_expr(stmt.target).text
            return [self._indent_line(f"{target} {stmt.op} {self._render_expr(stmt.value).text}", level)]
        if isinstance(stmt, ExprStmt):
            return [self._indent_line(self._render_expr(stmt.expr).text, level)]
        if isinstance(stmt, Return):
            if stmt.value is None:
                return [self._indent_line("return", level)]
            return [self._indent_line(f"return {self._render_expr(stmt.value).text}", level)]
        if isinstance(stmt, If):
            return self._render_if(stmt, level)
        if isinstance(stmt, While):
            return self._render_while(stmt, level)
        if isinstance(stmt, For):
            return self._render_for(stmt, level)
        if isinstance(stmt, BreakStmt):
            return [self._indent_line("break", level)]
        if isinstance(stmt, ContinueStmt):
            return [self._indent_line("continue", level)]
        if isinstance(stmt, IncDecStmt):
            op = "+= 1" if stmt.op == "++" else "-= 1"
            target = self._render_expr(stmt.var).text
            return [self._indent_line(f"{target} {op}", level)]
        if isinstance(stmt, SwitchStmt):
            return self._render_switch(stmt, level)
        if isinstance(stmt, Empty):
            return []
        raise TypeError(f"unsupported statement: {type(stmt)!r}")

    def _render_vardecl(self, node: VarDecl, level: int) -> list[str]:
        if node.array_size is not None and node.init is None:
            if node.type.startswith("int"):
                default = "0"
            elif node.type.startswith("float"):
                default = "0.0"
            else:
                default = "None"
            line = f"{node.name} = [{default}] * {self._render_expr(node.array_size).text}"
        elif node.init is None:
            if node.type.startswith("struct "):
                struct_name = node.type[len("struct "):]
                line = f"{node.name} = {struct_name}()"
            else:
                line = f"{node.name} = None"
        else:
            line = f"{node.name} = {self._render_expr(node.init).text}"
        return [self._indent_line(line, level)]

    def _render_struct(self, node: StructDef) -> list[str]:
        lines = [f"class {node.name}:"]
        if not node.fields:
            lines.append(self._indent_line("pass", 1))
            return lines
        lines.append(self._indent_line("def __init__(self):", 1))
        if not node.fields:
            lines.append(self._indent_line("pass", 2))
            return lines
        for field in node.fields:
            lines.append(self._indent_line(f"self.{field.name} = None", 2))
        return lines

    def _render_switch(self, node: SwitchStmt, level: int) -> list[str]:
        lines: list[str] = []
        switch_expr = self._render_expr(node.expr).text
        lines.append(self._indent_line(f"__switch_value = {switch_expr}", level))
        if not node.cases and node.default is None:
            lines.append(self._indent_line("pass", level))
            return lines
        for index, case in enumerate(node.cases):
            test = f"__switch_value == {self._render_expr(case.value).text}"
            if index == 0:
                lines.append(self._indent_line(f"if {test}:", level))
            else:
                lines.append(self._indent_line(f"elif {test}:", level))
            body_lines = self._render_statements(case.body, level + 1)
            if not body_lines:
                body_lines = [self._indent_line("pass", level + 1)]
            lines.extend(body_lines)
        if node.default is not None:
            lines.append(self._indent_line("else:", level))
            body_lines = self._render_statements(node.default.body, level + 1)
            if not body_lines:
                body_lines = [self._indent_line("pass", level + 1)]
            lines.extend(body_lines)
        return lines

    def _render_if(self, node: If, level: int) -> list[str]:
        lines: list[str] = []

        current = node
        first = True

        while True:

            keyword = "if" if first else "elif"

            lines.append(
                self._indent_line(
                    f"{keyword} {self._render_expr(current.condition).text}:",
                    level,
                )
            )

            body_lines = self._render_statements(
                current.then_body,
                level + 1,
            )

            if not body_lines:
                body_lines = [self._indent_line("pass", level + 1)]

            lines.extend(body_lines)

            else_body = current.else_body

            # elif chain
            if (
                else_body is not None
                and len(else_body) == 1
                and isinstance(else_body[0], If)
            ):
                current = else_body[0]
                first = False
                continue

            # final else
            if else_body is not None:
                lines.append(self._indent_line("else:", level))

                else_lines = self._render_statements(
                    else_body,
                    level + 1,
                )

                if not else_lines:
                    else_lines = [self._indent_line("pass", level + 1)]

                lines.extend(else_lines)

            break

        return lines

    def _render_while(self, node: While, level: int) -> list[str]:
        lines = [self._indent_line(f"while {self._render_expr(node.condition).text}:", level)]
        body_lines = self._render_statements(node.body, level + 1)
        if not body_lines:
            body_lines = [self._indent_line("pass", level + 1)]
        lines.extend(body_lines)
        return lines

    def _render_for(self, node: For, level: int) -> list[str]:
        lines: list[str] = []
        if node.init is not None:
            lines.extend(self._render_statement(node.init, level))
        cond_text = "True" if node.condition is None else self._render_expr(node.condition).text
        lines.append(self._indent_line(f"while {cond_text}:", level))
        body_lines = self._render_statements(node.body, level + 1)
        if node.post is not None:
            body_lines.extend(self._render_statement(node.post, level + 1))
        if not body_lines:
            body_lines = [self._indent_line("pass", level + 1)]
        lines.extend(body_lines)
        return lines

    def _render_expr(self, expr: Expr) -> Rendered:
        if isinstance(expr, Number):
            return Rendered(text=repr(expr.value), precedence=4)
        if isinstance(expr, String):
            return Rendered(text=repr(expr.value), precedence=4)
        if isinstance(expr, Boolean):
            return Rendered(text="True" if expr.value else "False", precedence=4)
        if isinstance(expr, Var):
            return Rendered(text=expr.name, precedence=4)
        if isinstance(expr, str):
            return Rendered(text=expr, precedence=4)
        if isinstance(expr, MemberAccess):
            base = self._render_expr(expr.base)
            return Rendered(text=f"{base.text}.{expr.member}", precedence=4)
        if isinstance(expr, IndexAccess):
            base = self._render_expr(expr.base)
            index = self._render_expr(expr.index)
            return Rendered(text=f"{base.text}[{index.text}]", precedence=4)
        if isinstance(expr, ListLiteral):
            items = ", ".join(self._render_expr(item).text for item in expr.elements)
            return Rendered(text=f"[{items}]", precedence=4)
        if isinstance(expr, Call):
            if expr.func == "printf" and expr.args:
                first = expr.args[0]
                args = expr.args[1:]
                if isinstance(first, String) and args:
                    fmt_text = first.value
                    arg_text = ", ".join(self._render_expr(arg).text for arg in args)
                    if len(args) == 1:
                        formatted_text = f"{repr(fmt_text)} % {arg_text}"
                    else:
                        formatted_text = f"{repr(fmt_text)} % ({arg_text})"
                    return Rendered(text=f"print({formatted_text}, end=\"\")", precedence=4)
            name = "print" if expr.func == "printf" else expr.func
            args = ", ".join(self._render_expr(arg).text for arg in expr.args)
            return Rendered(text=f"{name}({args})", precedence=4)
        if isinstance(expr, UnaryOp):
            operand = self._render_expr(expr.operand)
            text = operand.text
            if operand.precedence < 3:
                text = f"({text})"
            return Rendered(text=f"{expr.op} {text}" if expr.op == "not" else f"{expr.op}{text}", precedence=3)
        if isinstance(expr, BinaryOp):
            op = expr.op
            if op == "&&":
                op = "and"
            elif op == "||":
                op = "or"
            prec = self._binary_precedence(op)
            left = self._render_expr(expr.left)
            right = self._render_expr(expr.right)
            ltxt = left.text if left.precedence >= prec else f"({left.text})"
            rtxt = right.text if right.precedence > prec else f"({right.text})"
            return Rendered(text=f"{ltxt} {op} {rtxt}", precedence=prec)
        if isinstance(expr, TernaryOp):
            condition = self._render_expr(expr.condition)
            then_expr = self._render_expr(expr.then_expr)
            else_expr = self._render_expr(expr.else_expr)
            cond = condition.text
            if condition.precedence < 1:
                cond = f"({cond})"

            text = f"{then_expr.text} if {cond} else {else_expr.text}"
            return Rendered(text=text, precedence=0)
        raise TypeError(f"unsupported expression: {type(expr)!r}")

    def _binary_precedence(self, op: str) -> int:
        if op in ("*", "/"):
            return 4
        if op in ("+", "-"):
            return 3
        if op in ("==", "!=", "<", ">", "<=", ">="):
            return 2
        if op in ("and", "or"):
            return 1
        return 0

    def _indent_line(self, line: str, level: int) -> str:
        return f"{self.indent * level}{line}"

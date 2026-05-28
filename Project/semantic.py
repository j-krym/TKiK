from __future__ import annotations

from dataclasses import dataclass

from utils import (
    Assignment, BinaryOp, Boolean, BreakStmt, Call, CaseBlock, ContinueStmt,
    DefaultBlock, Expr, ExprStmt, For, FunctionDef, If, IncDecStmt, IndexAccess,
    ListLiteral, MemberAccess, Number, Param, Program, Return, Statement, String,
    StructDef, SwitchStmt, TernaryOp, UnaryOp, Var, VarDecl, While,
)


class SemanticError(Exception):
    """Raised when the source program is syntactically correct but semantically invalid."""


@dataclass(frozen=True)
class TypeInfo:
    name: str

    @property
    def category(self) -> str:
        return "int" if self.name == "int" else "non-int"


@dataclass(frozen=True)
class FunctionInfo:
    return_type: TypeInfo
    params: list[TypeInfo]


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.scopes: list[dict[str, TypeInfo]] = []
        self.functions: dict[str, FunctionInfo] = {
            "printf": FunctionInfo(TypeInfo("int"), []),
        }
        self.structs: dict[str, dict[str, TypeInfo]] = {}
        self.current_function: FunctionInfo | None = None
        self.loop_depth = 0
        self.switch_depth = 0

    def analyze(self, program: Program) -> None:
        self._push_scope()

        for item in program.items:
            if isinstance(item, StructDef):
                self._declare_struct(item)
            elif isinstance(item, FunctionDef):
                self._declare_function(item)
            elif isinstance(item, VarDecl):
                self._declare_var(item.name, TypeInfo(item.type))

        for item in program.items:
            if isinstance(item, VarDecl):
                self._check_var_decl(item, already_declared=True)
            elif isinstance(item, FunctionDef):
                self._check_function(item)

        self._pop_scope()

    def _push_scope(self) -> None:
        self.scopes.append({})

    def _pop_scope(self) -> None:
        self.scopes.pop()

    def _declare_var(self, name: str, type_info: TypeInfo) -> None:
        if name in self.scopes[-1]:
            raise SemanticError(f"Redeclaration of variable '{name}'")
        self.scopes[-1][name] = type_info

    def _lookup_var(self, name: str) -> TypeInfo:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Use of undeclared variable '{name}'")

    def _declare_struct(self, node: StructDef) -> None:
        name = f"struct {node.name}"
        if name in self.structs:
            raise SemanticError(f"Redeclaration of struct '{node.name}'")
        fields: dict[str, TypeInfo] = {}
        for field in node.fields:
            if field.name in fields:
                raise SemanticError(f"Redeclaration of field '{field.name}' in {name}")
            fields[field.name] = TypeInfo(field.type)
        self.structs[name] = fields

    def _declare_function(self, node: FunctionDef) -> None:
        if node.name in self.functions and node.name != "printf":
            raise SemanticError(f"Redeclaration of function '{node.name}'")
        self.functions[node.name] = FunctionInfo(
            return_type=TypeInfo(node.return_type),
            params=[TypeInfo(param.type) for param in node.params],
        )

    def _check_function(self, node: FunctionDef) -> None:
        self.current_function = self.functions[node.name]
        self._push_scope()
        for param in node.params:
            self._declare_var(param.name, TypeInfo(param.type))
        self._check_statements(node.body)
        self._pop_scope()
        self.current_function = None

    def _check_statements(self, statements: list[Statement]) -> None:
        for stmt in statements:
            self._check_statement(stmt)

    def _check_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, VarDecl):
            self._check_var_decl(stmt)
        elif isinstance(stmt, Assignment):
            self._check_assignment(stmt)
        elif isinstance(stmt, ExprStmt):
            self._expr_type(stmt.expr)
        elif isinstance(stmt, If):
            self._require_int(stmt.condition, "if condition")
            self._push_scope(); self._check_statements(stmt.then_body); self._pop_scope()
            if stmt.else_body is not None:
                self._push_scope(); self._check_statements(stmt.else_body); self._pop_scope()
        elif isinstance(stmt, While):
            self._require_int(stmt.condition, "while condition")
            self.loop_depth += 1
            self._push_scope(); self._check_statements(stmt.body); self._pop_scope()
            self.loop_depth -= 1
        elif isinstance(stmt, For):
            self._push_scope()
            if stmt.init is not None:
                self._check_statement(stmt.init)
            if stmt.condition is not None:
                self._require_int(stmt.condition, "for condition")
            self.loop_depth += 1
            self._check_statements(stmt.body)
            self.loop_depth -= 1
            if stmt.post is not None:
                self._check_statement(stmt.post)
            self._pop_scope()
        elif isinstance(stmt, Return):
            self._check_return(stmt)
        elif isinstance(stmt, IncDecStmt):
            self._require_exact_int(self._lookup_var(stmt.var), f"increment/decrement of '{stmt.var}'")
        elif isinstance(stmt, SwitchStmt):
            self._require_int(stmt.expr, "switch expression")
            self.switch_depth += 1
            for case in stmt.cases:
                self._check_case(case)
            if stmt.default is not None:
                self._check_default(stmt.default)
            self.switch_depth -= 1
        elif isinstance(stmt, BreakStmt):
            if self.loop_depth == 0 and self.switch_depth == 0:
                raise SemanticError("'break' used outside loop or switch")
        elif isinstance(stmt, ContinueStmt):
            if self.loop_depth == 0:
                raise SemanticError("'continue' used outside loop")

    def _check_case(self, case: CaseBlock) -> None:
        self._require_int(case.value, "case value")
        self._push_scope(); self._check_statements(case.body); self._pop_scope()

    def _check_default(self, default: DefaultBlock) -> None:
        self._push_scope(); self._check_statements(default.body); self._pop_scope()

    def _check_var_decl(self, node: VarDecl, already_declared: bool = False) -> None:
        declared_type = TypeInfo(node.type)
        if node.array_size is not None:
            self._require_int(node.array_size, f"array size of '{node.name}'")
        if node.init is not None:
            init_type = self._expr_type(node.init)
            self._require_same_category(declared_type, init_type, f"initialization of '{node.name}'")
        if not already_declared:
            self._declare_var(node.name, declared_type)

    def _check_assignment(self, node: Assignment) -> None:
        left_type = self._lvalue_type(node.target)
        right_type = self._expr_type(node.value)
        self._require_same_category(left_type, right_type, "assignment")
        if node.op != "=":
            self._require_exact_int(left_type, f"compound assignment '{node.op}'")
            self._require_exact_int(right_type, f"compound assignment '{node.op}'")

    def _check_return(self, node: Return) -> None:
        if self.current_function is None:
            return
        expected = self.current_function.return_type
        if expected.name == "void":
            if node.value is not None:
                raise SemanticError("Void function cannot return a value")
            return
        if node.value is None:
            raise SemanticError("Non-void function must return a value")
        actual = self._expr_type(node.value)
        self._require_same_category(expected, actual, "return statement")

    def _lvalue_type(self, expr: Expr) -> TypeInfo:
        if isinstance(expr, str):
            return self._lookup_var(expr)
        if isinstance(expr, Var):
            return self._lookup_var(expr.name)
        if isinstance(expr, IndexAccess):
            base_type = self._expr_type(expr.base)
            self._require_int(expr.index, "array index")
            if base_type.name.endswith("[]"):
                return TypeInfo(base_type.name[:-2])
            return base_type
        if isinstance(expr, MemberAccess):
            return self._member_type(expr)
        raise SemanticError("Left side of assignment is not assignable")

    def _expr_type(self, expr: Expr) -> TypeInfo:
        if isinstance(expr, Number):
            return TypeInfo("int" if isinstance(expr.value, int) else "float")
        if isinstance(expr, String):
            return TypeInfo("string")
        if isinstance(expr, Boolean):
            return TypeInfo("int")
        if isinstance(expr, Var):
            return self._lookup_var(expr.name)
        if isinstance(expr, ListLiteral):
            for element in expr.elements:
                self._expr_type(element)
            return TypeInfo("list")
        if isinstance(expr, IndexAccess):
            return self._lvalue_type(expr)
        if isinstance(expr, MemberAccess):
            return self._member_type(expr)
        if isinstance(expr, UnaryOp):
            inner = self._expr_type(expr.operand)
            self._require_exact_int(inner, f"unary operator '{expr.op}'")
            return TypeInfo("int")
        if isinstance(expr, BinaryOp):
            return self._binary_type(expr)
        if isinstance(expr, TernaryOp):
            self._require_int(expr.condition, "ternary condition")
            t1 = self._expr_type(expr.then_expr)
            t2 = self._expr_type(expr.else_expr)
            self._require_same_category(t1, t2, "ternary branches")
            return t1
        if isinstance(expr, Call):
            return self._call_type(expr)
        raise SemanticError(f"Unsupported expression: {type(expr).__name__}")

    def _binary_type(self, expr: BinaryOp) -> TypeInfo:
        left = self._expr_type(expr.left)
        right = self._expr_type(expr.right)
        if expr.op in {"+", "-", "*", "/", "%"}:
            self._require_exact_int(left, f"operator '{expr.op}'")
            self._require_exact_int(right, f"operator '{expr.op}'")
            return TypeInfo("int")
        if expr.op in {"<", ">", "<=", ">=", "==", "!="}:
            self._require_same_category(left, right, f"comparison '{expr.op}'")
            return TypeInfo("int")
        if expr.op in {"&&", "||"}:
            self._require_exact_int(left, f"logical operator '{expr.op}'")
            self._require_exact_int(right, f"logical operator '{expr.op}'")
            return TypeInfo("int")
        raise SemanticError(f"Unknown operator '{expr.op}'")

    def _member_type(self, expr: MemberAccess) -> TypeInfo:
        base_type = self._expr_type(expr.base)
        fields = self.structs.get(base_type.name)
        if fields is None:
            raise SemanticError(f"Type '{base_type.name}' has no fields")
        if expr.member not in fields:
            raise SemanticError(f"Type '{base_type.name}' has no field '{expr.member}'")
        return fields[expr.member]

    def _call_type(self, expr: Call) -> TypeInfo:
        if expr.func not in self.functions:
            raise SemanticError(f"Call to undeclared function '{expr.func}'")
        info = self.functions[expr.func]
        if expr.func != "printf":
            if len(expr.args) != len(info.params):
                raise SemanticError(
                    f"Function '{expr.func}' expects {len(info.params)} arguments, got {len(expr.args)}"
                )
            for i, (arg, expected) in enumerate(zip(expr.args, info.params), start=1):
                actual = self._expr_type(arg)
                self._require_same_category(expected, actual, f"argument {i} of '{expr.func}'")
        else:
            for arg in expr.args:
                self._expr_type(arg)
        return info.return_type

    def _require_int(self, expr: Expr, context: str) -> None:
        self._require_exact_int(self._expr_type(expr), context)

    def _require_exact_int(self, type_info: TypeInfo, context: str) -> None:
        if type_info.name != "int":
            raise SemanticError(f"Expected int in {context}, got {type_info.name}")

    def _require_same_category(self, expected: TypeInfo, actual: TypeInfo, context: str) -> None:
        if expected.category != actual.category:
            raise SemanticError(
                f"Type mismatch in {context}: expected {expected.category}, got {actual.category}"
            )

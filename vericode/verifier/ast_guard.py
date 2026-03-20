"""
Deterministic AST Anti-Tampering Guard.
Prevents models from exploiting test runners, monkeypatching assertions, or tampering with harnesses.
"""

import ast
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ASTSecurityViolation:
    line_number: int
    rule: str
    description: str


class ASTGuardVisitor(ast.NodeVisitor):
    """Inspects AST nodes for security and anti-cheating violations."""

    FORBIDDEN_CALLS = {
        "exec",
        "eval",
        "__import__",
        "compile",
    }

    FORBIDDEN_MODULES = {
        "unittest.mock",
        "mock",
        "subprocess",
        "shutil",
    }

    def __init__(self):
        self.violations: List[ASTSecurityViolation] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name in self.FORBIDDEN_MODULES:
                self.violations.append(
                    ASTSecurityViolation(
                        line_number=node.lineno,
                        rule="FORBIDDEN_IMPORT",
                        description=f"Direct import of '{alias.name}' is prohibited in verifier scope.",
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        if any(module == forbidden or module.startswith(forbidden + ".") for forbidden in self.FORBIDDEN_MODULES):
            self.violations.append(
                ASTSecurityViolation(
                    line_number=node.lineno,
                    rule="FORBIDDEN_IMPORT_FROM",
                    description=f"Importing from '{module}' is prohibited in verifier scope.",
                )
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_CALLS:
                self.violations.append(
                    ASTSecurityViolation(
                        line_number=node.lineno,
                        rule="DYNAMIC_CODE_EXECUTION",
                        description=f"Calling '{node.func.id}()' violates deterministic execution constraints.",
                    )
                )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # Prevent tampering with sys.modules or __builtins__
        if node.attr in {"__builtins__", "modules"}:
            if isinstance(node.value, ast.Name) and node.value.id in {"sys", "__builtins__"}:
                self.violations.append(
                    ASTSecurityViolation(
                        line_number=node.lineno,
                        rule="RUNTIME_TAMPERING",
                        description="Tampering with interpreter internals or sys.modules is prohibited.",
                    )
                )
        self.generic_visit(node)


def inspect_code_ast(source_code: str) -> Tuple[bool, List[ASTSecurityViolation]]:
    """
    Parse source code and assert it passes AST safety and anti-cheating invariants.

    Returns:
        (is_safe, list_of_violations)
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return False, [
            ASTSecurityViolation(
                line_number=e.lineno or 1,
                rule="SYNTAX_ERROR",
                description=f"Code fails to parse: {e.msg}",
            )
        ]

    visitor = ASTGuardVisitor()
    visitor.visit(tree)
    return len(visitor.violations) == 0, visitor.violations

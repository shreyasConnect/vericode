"""
Tests for AST Anti-Tampering Guard.
"""

from vericode.verifier.ast_guard import inspect_code_ast


def test_clean_code_passes():
    code = """
def add(a, b):
    return a + b
"""
    is_safe, violations = inspect_code_ast(code)
    assert is_safe is True
    assert len(violations) == 0


def test_syntax_error_detected():
    bad_syntax = "def broken(: return 1"
    is_safe, violations = inspect_code_ast(bad_syntax)
    assert is_safe is False
    assert any(v.rule == "SYNTAX_ERROR" for v in violations)


def test_exec_eval_blocked():
    code_exec = """
def hack():
    exec("import os; os.system('echo hacked')")
"""
    is_safe, violations = inspect_code_ast(code_exec)
    assert is_safe is False
    assert any(v.rule == "DYNAMIC_CODE_EXECUTION" for v in violations)


def test_forbidden_mock_import_blocked():
    code_mock = """
from unittest.mock import patch

def fake_test():
    with patch("something"):
        pass
"""
    is_safe, violations = inspect_code_ast(code_mock)
    assert is_safe is False
    assert any(v.rule == "FORBIDDEN_IMPORT_FROM" for v in violations)


def test_sys_modules_tamper_blocked():
    code_tamper = """
import sys

def hijack():
    sys.modules['my_module'] = None
"""
    is_safe, violations = inspect_code_ast(code_tamper)
    assert is_safe is False
    assert any(v.rule == "RUNTIME_TAMPERING" for v in violations)

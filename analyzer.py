from __future__ import annotations

import ast
from typing import Any


RULES_VERSION = "0.1"


def _snippet(lines: list[str], line_no: int) -> str:
    start = max(1, line_no - 1)
    end = min(len(lines), line_no + 1)
    return "\n".join(f"{i}: {lines[i - 1]}" for i in range(start, end + 1))


def _finding(
    rule_id: str,
    title: str,
    severity: str,
    line: int,
    evidence: str,
    fix_guidance: str,
    lines: list[str],
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "title": title,
        "severity": severity,
        "line": line,
        "evidence": evidence,
        "fix_guidance": fix_guidance,
        "snippet": _snippet(lines, line),
    }


def analyze_code(code: str) -> dict[str, Any]:
    """Run deterministic AST-based rules against Python source code."""
    lines = code.splitlines()
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {
            "rules_version": RULES_VERSION,
            "syntax_error": f"line {exc.lineno}: {exc.msg}",
            "findings": [],
        }

    findings: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        # Hardcoded credential-like assignments.
        if isinstance(node, ast.Assign):
            names = []
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.append(target.id.lower())

            credential_words = ("password", "passwd", "secret", "api_key", "apikey", "token")
            if any(any(word in name for word in credential_words) for name in names):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    findings.append(
                        _finding(
                            "SEC001",
                            "Hardcoded credential detected",
                            "High",
                            node.lineno,
                            "A credential-like variable is assigned a literal string in source code.",
                            "Move the secret to an environment variable or a proper secret manager and load it at runtime.",
                            lines,
                        )
                    )

        # Dynamic execution.
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            findings.append(
                _finding(
                    "SEC002",
                    f"Dynamic execution using {node.func.id}()",
                    "High",
                    node.lineno,
                    f"The program calls {node.func.id}() on runtime data, which can execute arbitrary Python code.",
                    "Avoid eval/exec for untrusted input. Replace it with a safe parser or an explicit allowlist of supported operations.",
                    lines,
                )
            )

        # subprocess shell=True.
        if isinstance(node, ast.Call):
            is_subprocess = isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess"
            if is_subprocess:
                for keyword in node.keywords:
                    if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        findings.append(
                            _finding(
                                "SEC003",
                                "subprocess called with shell=True",
                                "High",
                                node.lineno,
                                "The subprocess call enables a shell to interpret the command string.",
                                "Prefer a list of arguments with shell=False (the default) and validate any user-controlled values.",
                                lines,
                            )
                        )

        # Bare except.
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append(
                _finding(
                    "QUAL001",
                    "Bare except can hide unexpected failures",
                    "Medium",
                    node.lineno,
                    "The handler catches every exception, including errors that may indicate programming defects.",
                    "Catch specific exception types and handle only failures you can recover from.",
                    lines,
                )
            )

        # Mutable default arguments.
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defaults = list(node.args.defaults)
            for default in defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    findings.append(
                        _finding(
                            "QUAL002",
                            "Mutable default argument",
                            "Medium",
                            node.lineno,
                            "A list, dict, or set is used as a function default value and can retain state across calls.",
                            "Use None as the default and create the mutable object inside the function.",
                            lines,
                        )
                    )

    findings.sort(key=lambda item: (item["line"], item["rule_id"]))
    return {
        "rules_version": RULES_VERSION,
        "syntax_error": None,
        "findings": findings,
    }

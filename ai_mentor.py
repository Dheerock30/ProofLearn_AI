from __future__ import annotations

import os

from google import genai


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=api_key)


def explain_finding(code: str, finding: dict, difficulty: str = "Beginner") -> str:
    """Ask Gemini to explain an already-detected finding.

    The prompt deliberately treats the deterministic finding as the source of truth.
    Gemini explains the finding instead of independently inventing a finding.
    """
    prompt = f"""
You are the explanation layer of ProofLearn AI, a beginner-friendly code review tool.

IMPORTANT:
- Do not invent a new vulnerability or claim a problem that is not in the supplied finding.
- Treat the supplied deterministic finding as the source of truth.
- Explain only what the finding and code support.
- Do not say the code is fully secure or correct.
- Use {difficulty.lower()} language.

DETERMINISTIC FINDING:
Rule: {finding['rule_id']}
Title: {finding['title']}
Severity: {finding['severity']}
Line: {finding['line']}
Evidence: {finding['evidence']}

CODE:
```python
{code}
```

Write a concise explanation in this structure:
1. What is wrong?
2. Why does it matter?
3. What should the beginner do?
Do not output code unless a tiny example is necessary.
""".strip()

    client = _client()
    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned no text")
    return text.strip()


def generate_fallback_explanation(finding: dict) -> str:
    return (
        f"This issue was detected by our deterministic rule `{finding['rule_id']}`. "
        f"{finding['evidence']} The safe next step is: {finding['fix_guidance']}"
    )

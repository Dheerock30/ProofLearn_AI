import os

try:
    from google import genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False


def get_level_instruction(level):
    """Return instructions based on the selected explanation level."""
    instructions = {
        "Beginner": (
            "Explain using simple language. Assume the user is new to Python. "
            "Avoid unnecessary jargon. Explain step by step and use a simple example."
        ),
        "Intermediate": (
            "Explain for someone who understands Python fundamentals. "
            "Include the relevant programming concept, why the behavior occurs, "
            "possible consequences, and a practical solution."
        ),
        "Advanced": (
            "Provide a technically detailed explanation. Discuss Python semantics, "
            "runtime behavior, edge cases, design trade-offs, maintainability, "
            "and best practices. Use precise technical terminology."
        )
    }
    return instructions.get(level, instructions["Beginner"])


def generate_fallback_explanation(finding, level="Beginner", error_msg=None):
    """Generate explanation when Gemini is unavailable, showing the debug error if present."""
    rule = finding.get("rule", "Unknown Rule")
    message = finding.get("message", "A potential issue was detected.")
    explanation = finding.get("explanation", "This code pattern may lead to unexpected behavior.")
    suggestion = finding.get("suggestion", "Review the code and use a safer implementation.")

    debug_banner = f"""
> ⚠️ **Gemini API Debug Notice:** 
> `{error_msg}`
> *Check your terminal console, API key permissions, or billing/quota status.*
---
""" if error_msg else ""

    return debug_banner + f"""
## What was detected?

**{message}**

### Why is this a problem?

{explanation}

### How can you fix it?

{suggestion}

### Simple takeaway

Try to write code that behaves predictably and is easy to understand.
"""


def explain_finding(finding, level="Beginner"):
    """Generate an AI explanation for a detected finding."""
    level_instruction = get_level_instruction(level)
    api_key = os.getenv("GEMINI_API_KEY")

    if not GEMINI_AVAILABLE:
        return generate_fallback_explanation(finding, level, "Library `google-genai` is not imported or installed properly.")
    
    if not api_key:
        return generate_fallback_explanation(finding, level, "Environment variable `GEMINI_API_KEY` is missing or empty.")

    try:
        client = genai.Client(api_key=api_key)

        rule = finding.get("rule", "Unknown Rule")
        message = finding.get("message", "")
        explanation = finding.get("explanation", "")
        suggestion = finding.get("suggestion", "")
        code = finding.get("code", "")

        prompt = f"""
You are ProofLearn AI, an educational programming mentor.
A static code analysis system detected an issue.

Rule: {rule}
Detected Issue: {message}
Technical Explanation: {explanation}
Recommended Fix: {suggestion}
Code Context: {code}

The user selected this explanation level: {level}
Instructions for this level: {level_instruction}

Structure your response as follows:
1. What was detected
2. Why it happens
3. Why it matters
4. How to fix it
5. Corrected example
"""
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        if response and response.text:
            return response.text

        return generate_fallback_explanation(finding, level, "API returned an empty response.")

    except Exception as error:
        print("Gemini error details:", error)
        return generate_fallback_explanation(finding, level, str(error))

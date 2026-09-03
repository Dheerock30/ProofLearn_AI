from __future__ import annotations


def build_understanding_check(finding: dict) -> dict:
    rule_id = finding["rule_id"]

    quizzes = {
        "SEC001": {
            "question": "Why is storing a password or API key directly in source code risky?",
            "options": [
                "Anyone who gets the source code may be able to see the secret.",
                "Python will always delete the password after the program ends.",
                "The string becomes encrypted automatically by Python.",
                "It only affects the code's formatting.",
            ],
            "answer": "Anyone who gets the source code may be able to see the secret.",
        },
        "SEC002": {
            "question": "Why can eval() be dangerous when the expression comes from a user?",
            "options": [
                "It can execute Python code that the user supplied.",
                "It always makes programs slower than print().",
                "It changes all strings to integers.",
                "It prevents exceptions from being raised.",
            ],
            "answer": "It can execute Python code that the user supplied.",
        },
        "SEC003": {
            "question": "Why is shell=True risky when command content can be influenced by a user?",
            "options": [
                "Shell metacharacters can change what command gets executed.",
                "It automatically encrypts command arguments.",
                "It makes Python syntax invalid.",
                "It disables every subprocess call.",
            ],
            "answer": "Shell metacharacters can change what command gets executed.",
        },
        "QUAL001": {
            "question": "Why is a bare except usually a maintainability problem?",
            "options": [
                "It can hide unexpected errors that should be visible during debugging.",
                "It guarantees the application will crash.",
                "It only catches syntax errors.",
                "It prevents all exceptions from occurring.",
            ],
            "answer": "It can hide unexpected errors that should be visible during debugging.",
        },
        "QUAL002": {
            "question": "Why can a mutable default argument cause surprising behavior?",
            "options": [
                "The same mutable object can be reused across function calls.",
                "Python converts every list into a tuple.",
                "The function cannot accept parameters.",
                "Mutable objects are always read-only.",
            ],
            "answer": "The same mutable object can be reused across function calls.",
        },
    }
    return quizzes.get(rule_id, {
        "question": "What is the main reason this finding matters?",
        "options": [
            "It represents a concrete issue identified by a review rule.",
            "It is only a formatting preference.",
            "It guarantees the program is malicious.",
            "It means Python cannot run the file.",
        ],
        "answer": "It represents a concrete issue identified by a review rule.",
    })


def evaluate_understanding(quiz: dict, selected: str) -> tuple[bool, str]:
    correct = selected == quiz["answer"]
    if correct:
        return True, "✅ Correct — you identified the root cause."
    return False, "Not quite. The answer should explain the underlying risk, not just the symptom."

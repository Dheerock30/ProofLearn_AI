import json
import os
from typing import Any

import streamlit as st

from analyzer import analyze_code
from ai_mentor import explain_finding, generate_fallback_explanation
from understanding import build_understanding_check, evaluate_understanding

st.set_page_config(page_title="ProofLearn AI", page_icon="🛡️", layout="wide")

st.title("🛡️ ProofLearn AI")
st.caption("Understand the code. Verify the issue. Fix it safely.")

with st.sidebar:
    st.header("Review settings")
    use_ai = st.toggle("Use Gemini explanation", value=True)
    difficulty = st.selectbox("Explanation level", ["Beginner", "Intermediate"], index=0)
    st.markdown("**Core loop:** Detect → Explain → Verify → Fix")

DEFAULT_CODE = '''# Example: unsafe hardcoded credential\npassword = "admin123"\n\nuser_input = input("Enter an expression: ")\nresult = eval(user_input)\nprint(result)\n'''

code = st.text_area("Paste Python code", value=DEFAULT_CODE, height=320, key="code")

if st.button("🔎 Review Code", type="primary", use_container_width=True):
    st.session_state["analysis"] = analyze_code(code)
    st.session_state["reviewed_code"] = code

analysis: dict[str, Any] | None = st.session_state.get("analysis")

if analysis:
    if analysis["syntax_error"]:
        st.error(f"Syntax error: {analysis['syntax_error']}")
        st.info("Fix the syntax first, then run the review again.")
    else:
        findings = analysis["findings"]
        st.metric("Issues found", len(findings))

        if not findings:
            st.success("No issues were detected by the current deterministic rules.")
            st.caption("This is not a guarantee of secure or bug-free code.")
        else:
            for index, finding in enumerate(findings, start=1):
                with st.container(border=True):
                    st.markdown(f"### {index}. {finding['title']}")
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Severity:** {finding['severity']}")
                    c2.write(f"**Line:** {finding['line']}")
                    c3.write(f"**Rule:** `{finding['rule_id']}`")
                    st.code(finding["snippet"], language="python")
                    st.write(f"**Evidence:** {finding['evidence']}")

                    explanation_key = f"explanation_{index}"
                    if explanation_key not in st.session_state:
                        if use_ai and os.getenv("GEMINI_API_KEY"):
                            with st.spinner("Generating beginner-friendly explanation..."):
                                try:
                                    st.session_state[explanation_key] = explain_finding(
                                        code=st.session_state["reviewed_code"],
                                        finding=finding,
                                        difficulty=difficulty,
                                    )
                                except Exception as exc:
                                    st.session_state[explanation_key] = generate_fallback_explanation(finding)
                                    st.warning(f"Gemini unavailable, using deterministic fallback. ({type(exc).__name__})")
                        else:
                            st.session_state[explanation_key] = generate_fallback_explanation(finding)

                    st.markdown("**Explanation**")
                    st.write(st.session_state[explanation_key])

                    quiz = build_understanding_check(finding)
                    answer_key = f"answer_{index}"
                    submitted_key = f"submitted_{index}"
                    selected = st.radio(
                        quiz["question"],
                        quiz["options"],
                        index=None,
                        key=f"radio_{index}",
                    )
                    if st.button("Check my understanding", key=f"check_{index}"):
                        if selected is None:
                            st.warning("Choose an answer first.")
                        else:
                            correct, feedback = evaluate_understanding(quiz, selected)
                            st.session_state[submitted_key] = True
                            st.session_state[answer_key] = selected
                            if correct:
                                st.success(feedback)
                                st.markdown("**Guided fix**")
                                st.write(finding["fix_guidance"])
                            else:
                                st.error(feedback)
                                st.info("Review the explanation above and try again.")

        with st.expander("Technical details"):
            st.json(analysis)

st.divider()
st.caption("Prototype: deterministic findings are the source of truth for detected issues; Gemini is used for explanation and guidance.")

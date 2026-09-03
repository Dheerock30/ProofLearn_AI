import time
import streamlit as st
from dotenv import load_dotenv

from analyzer import analyze_code
from ai_mentor import explain_finding, generate_fallback_explanation
from understanding import build_understanding_check, evaluate_understanding

# Initialize environment variables
load_dotenv()

# -----------------------------
# Enterprise Page Configuration
# -----------------------------
st.set_page_config(
    page_title="ProofLearn Studio",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Advanced UI Injection (CSS)
# -----------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Typography & Theme */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #ededed;
        background-color: #0e0e10;
    }
    code, .stTextArea textarea {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
        background-color: #141416 !important;
        color: #f3f4f6 !important;
        border: 1px solid #27272a !important;
        border-radius: 6px !important;
    }

    /* Minimalist Layout Adjustments */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 96%;
    }

    /* Containers and Cards */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: #121214;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background: #141416;
        border: 1px solid #27272a;
        border-radius: 6px;
        padding: 0.75rem 1rem;
    }
    div[data-testid="stMetric"] label {
        color: #a1a1aa !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f4f4f5 !important;
        font-size: 1.25rem !important;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #27272a;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 0.85rem;
        color: #a1a1aa;
        padding: 0.5rem 0rem;
        background-color: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #f4f4f5 !important;
        border-bottom: 2px solid #f4f4f5;
    }

    /* Buttons */
    .stButton > button {
        background-color: #18181b;
        color: #f4f4f5;
        border: 1px solid #27272a;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.85rem;
        transition: background-color 0.15s ease;
    }
    .stButton > button:hover {
        background-color: #27272a;
        border-color: #3f3f46;
        color: #ffffff;
    }
    button[kind="primary"] {
        background-color: #f4f4f5 !important;
        color: #09090b !important;
        font-weight: 600 !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background-color: #e4e4e7 !important;
    }

    /* Severity Badges */
    .badge-high { 
        background-color: rgba(239, 68, 68, 0.1); 
        color: #f87171; 
        border: 1px solid rgba(239, 68, 68, 0.2);
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 0.7rem; 
        font-weight: 600; 
        letter-spacing: 0.05em;
    }
    .badge-med { 
        background-color: rgba(234, 179, 8, 0.1); 
        color: #facc15; 
        border: 1px solid rgba(234, 179, 8, 0.2);
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 0.7rem; 
        font-weight: 600; 
        letter-spacing: 0.05em;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Demo Snippets
# -----------------------------
SNIPPET_1 = """# Demo 1: Hardcoded Secrets & Dynamic Execution (SEC001 & SEC002)
def process_user_data(user_input):
    # Authenticate via hardcoded token
    api_key = "sk_live_98a7b6c5d4e3f2a1"
    
    # Evaluate dynamic query
    query_result = eval(user_input)
    
    return query_result
"""

SNIPPET_2 = """# Demo 2: Subprocess Shell & Bare Except (SEC003 & QUAL001)
import subprocess

def ping_server(ip_address):
    try:
        # User controls ip_address entirely
        subprocess.run(f"ping -c 4 {ip_address}", shell=True)
    except:
        # Silently fails on all errors
        print("Something went wrong!")
"""

SNIPPET_3 = """# Demo 3: Mutable Default Arguments (QUAL002)
def add_item_to_cart(item, cart=[]):
    # The 'cart' list retains state across multiple function calls
    cart.append(item)
    return cart
"""

# -----------------------------
# Session State Initialization
# -----------------------------
if "code" not in st.session_state:
    st.session_state.code = SNIPPET_1
if "analysis" not in st.session_state: st.session_state.analysis = None
if "reviewed_code" not in st.session_state: st.session_state.reviewed_code = None
if "explanations" not in st.session_state: st.session_state.explanations = {}
if "quiz_results" not in st.session_state: st.session_state.quiz_results = {}

# -----------------------------
# App Header
# -----------------------------
col_title, col_meta = st.columns([3, 1])
with col_title:
    st.markdown("### ProofLearn Studio")
    st.caption("Deterministic Code Review & Autonomous Mentorship Engine")
with col_meta:
    difficulty = st.selectbox(
        "Mentorship Depth",
        ["Beginner", "Intermediate", "Advanced"],
        label_visibility="collapsed"
    )

st.divider()

# -----------------------------
# Main Application Layout
# -----------------------------
col_editor, col_inspector = st.columns([1.1, 1.4], gap="large")

# --- LEFT PANE: EDITOR ---
with col_editor:
    st.markdown("#### Source Workspace")
    
    current_code = st.text_area(
        "Code Input",
        value=st.session_state.code,
        height=460,
        label_visibility="collapsed"
    )
    st.session_state.code = current_code

    st.markdown("<div style='font-size: 0.75rem; color: #a1a1aa; margin-top: 8px; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em;'>Preset Samples</div>", unsafe_allow_html=True)
    btn1, btn2, btn3 = st.columns(3)
    with btn1:
        if st.button("Sample 1: Sec", use_container_width=True):
            st.session_state.code = SNIPPET_1
            st.session_state.analysis = None
            st.rerun()
    with btn2:
        if st.button("Sample 2: Shell", use_container_width=True):
            st.session_state.code = SNIPPET_2
            st.session_state.analysis = None
            st.rerun()
    with btn3:
        if st.button("Sample 3: State", use_container_width=True):
            st.session_state.code = SNIPPET_3
            st.session_state.analysis = None
            st.rerun()

    st.write("") 

    action_col1, action_col2 = st.columns([2, 1])
    with action_col1:
        if st.button("Run Security Audit", type="primary", use_container_width=True):
            if current_code.strip():
                with st.spinner("Analyzing Abstract Syntax Tree..."):
                    time.sleep(0.3)
                    try:
                        st.session_state.analysis = analyze_code(current_code) 
                        st.session_state.reviewed_code = current_code
                        st.session_state.explanations.clear()
                        st.session_state.quiz_results.clear()
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Kernel Error: {exc}")
            else:
                st.warning("Editor is empty.")
                
    with action_col2:
        if st.button("Clear Workspace", use_container_width=True):
            st.session_state.code = ""
            st.session_state.analysis = None
            st.rerun()

# --- RIGHT PANE: TELEMETRY ---
with col_inspector:
    st.markdown("#### Inspection Telemetry")
    analysis = st.session_state.analysis
    
    if analysis is None:
        st.markdown("<div style='padding: 3rem 0; text-align: color: #71717a; font-size: 0.9rem;'>System idle. Run an audit to initialize diagnostic trace.</div>", unsafe_allow_html=True)
    
    elif analysis.get("syntax_error"):
        st.error(f"Syntax Error Intercepted: Line {analysis['syntax_error']}")
        
    else:
        findings = analysis.get("findings", []) 
        high_sev = sum(1 for f in findings if f.get("severity") == "High")
        med_sev = sum(1 for f in findings if f.get("severity") == "Medium")

        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Status", "Failed" if findings else "Passed")
        t2.metric("Total Flags", len(findings))
        t3.metric("Critical", high_sev)
        t4.metric("Warnings", med_sev)
        
        st.write("")

        if not findings:
            st.success("Zero deterministic violations found. AST structural analysis passed.")
        else:
            for idx, finding in enumerate(findings):
                rule_id = finding.get("rule_id", "UNKNOWN")
                sev = finding.get("severity", "Medium")
                badge_class = "badge-high" if sev == "High" else "badge-med"
                key = f"{idx}_{rule_id}"

                with st.container(border=True):
                    st.markdown(f"""
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                            <span style='font-weight: 500; font-size: 0.9rem;'>{finding.get('title')}</span>
                            <span class='{badge_class}'>{sev.upper()} // {rule_id}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    t_trace, t_mentor, t_fix = st.tabs(["Stack Trace", "AI Mentor", "Verify & Remediate"])
                    
                    with t_trace:
                        st.markdown(f"<div style='font-size: 0.8rem; color: #a1a1aa;'>Trigger Line: {finding.get('line', '?')}</div>", unsafe_allow_html=True)
                        st.code(finding.get("snippet", ""), language="python") 
                        st.markdown(f"<div style='font-size: 0.85rem; color: #d4d4d8;'>{finding.get('evidence', '')}</div>", unsafe_allow_html=True)

                    with t_mentor:
                        if key not in st.session_state.explanations:
                            if st.button("Request Contextual Breakdown", key=f"btn_exp_{key}"):
                                with st.spinner("Connecting to LLM Engine..."):
                                    mapped_finding = {
                                        "rule": finding.get("rule_id", "Unknown"),
                                        "message": finding.get("title", "Issue Detected"),
                                        "explanation": finding.get("evidence", "No evidence provided."),
                                        "suggestion": finding.get("fix_guidance", "Review standard protocols."),
                                        "code": finding.get("snippet", "")
                                    }
                                    
                                    try:
                                        expl = explain_finding(mapped_finding, level=difficulty) 
                                    except Exception as err:
                                        expl = generate_fallback_explanation(mapped_finding, level=difficulty, error_msg=str(err))
                                    
                                    st.session_state.explanations[key] = expl
                                    st.rerun()
                        else:
                            st.markdown(st.session_state.explanations[key])

                    with t_fix:
                        quiz = build_understanding_check(finding)
                        st.markdown(f"<div style='font-size: 0.85rem; font-weight: 500; margin-bottom: 8px;'>Knowledge Check: {quiz['question']}</div>", unsafe_allow_html=True)
                        
                        selected = st.radio(
                            "Select response",
                            quiz["options"],
                            key=f"radio_{key}",
                            label_visibility="collapsed"
                        )
                        
                        if st.button("Submit Response", key=f"btn_chk_{key}"):
                            correct, msg = evaluate_understanding(quiz, selected) 
                            st.session_state.quiz_results[key] = correct
                            if correct:
                                st.success(msg)
                            else:
                                st.error(msg)

                        if st.session_state.quiz_results.get(key, False):
                            st.divider()
                            st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #4ade80; margin-bottom: 4px;'>Approved Remediation Path</div>", unsafe_allow_html=True)
                            st.info(finding.get('fix_guidance', 'Review standard protocols.'))

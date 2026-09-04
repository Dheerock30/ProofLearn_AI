import time
import json
from datetime import datetime
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
    initial_sidebar_state="expanded"
)

# -----------------------------
# Advanced UI Injection & Professional Palette (CSS)
# -----------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Typography & Deep Obsidian Theme */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #f1f5f9;
        background-color: #090a0f;
    }
    code, .stTextArea textarea {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
        background-color: #0d0e12 !important;
        color: #38bdf8 !important;
        border: 1px solid #1e222d !important;
        border-radius: 8px !important;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }

    /* Minimalist Layout Adjustments (Preserving Header Toggle) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background-color: transparent !important;}
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 96%;
    }

    /* High-End Containers and Cards */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: #12141a;
        border: 1px solid #1e222d;
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }

    /* Sleek Metrics Styling */
    div[data-testid="stMetric"] {
        background: #12141a;
        border: 1px solid #1e222d;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 1.35rem !important;
        font-weight: 600;
    }
    
    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #1e222d;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 0.85rem;
        color: #94a3b8;
        padding: 0.5rem 0rem;
        background-color: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8;
    }

    /* Interactive Buttons */
    .stButton > button {
        background-color: #161922;
        color: #e2e8f0;
        border: 1px solid #262b3a;
        border-radius: 7px;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton > button:hover {
        background-color: #1e222d;
        border-color: #3b82f6;
        color: #ffffff;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.15);
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }

    /* Professional Severity Badges */
    .badge-high { 
        background-color: rgba(239, 68, 68, 0.12); 
        color: #f87171; 
        border: 1px solid rgba(239, 68, 68, 0.25);
        padding: 3px 10px; 
        border-radius: 6px; 
        font-size: 0.7rem; 
        font-weight: 600; 
        letter-spacing: 0.05em;
    }
    .badge-med { 
        background-color: rgba(234, 179, 8, 0.12); 
        color: #facc15; 
        border: 1px solid rgba(234, 179, 8, 0.25);
        padding: 3px 10px; 
        border-radius: 6px; 
        font-size: 0.7rem; 
        font-weight: 600; 
        letter-spacing: 0.05em;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Demo Snippets & Secure Patches
# -----------------------------
SNIPPET_1 = """# Demo 1: Hardcoded Secrets & Dynamic Execution (SEC001 & SEC002)
def process_user_data(user_input):
    # Authenticate via hardcoded token
    api_key = "sk_live_98a7b6c5d4e3f2a1"
    
    # Evaluate dynamic query
    query_result = eval(user_input)
    
    return query_result
"""
SECURE_1 = """# Remediated Code: Secure Configuration & Parsing
import os

def process_user_data(user_input):
    # Loaded safely from runtime environment variables
    api_key = os.getenv("AQ.Ab8RN6J9GVW4iTnihcxynTb4smclXfmdZ5C87eE-dgbB1gE4PA")
    
    # Safe numerical parsing instead of dynamic execution
    try:
        query_result = int(user_input)
    except ValueError:
        query_result = None
        
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
SECURE_2 = """# Remediated Code: Safe Subprocess & Explicit Exception Handling
import subprocess

def ping_server(ip_address):
    try:
        # Shell execution disabled and arguments passed as an explicit list
        subprocess.run(["ping", "-c", "4", ip_address], shell=False, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ping failed with exit code: {e.returncode}")
"""

SNIPPET_3 = """# Demo 3: Mutable Default Arguments (QUAL002)
def add_item_to_cart(item, cart=[]):
    # The 'cart' list retains state across multiple function calls
    cart.append(item)
    return cart
"""
SECURE_3 = """# Remediated Code: Immutable Default Arguments
def add_item_to_cart(item, cart=None):
    if cart is None:
        cart = []
    cart.append(item)
    return cart
"""

# -----------------------------
# Session State Initialization
# -----------------------------
if "code" not in st.session_state: st.session_state.code = SNIPPET_1
if "analysis" not in st.session_state: st.session_state.analysis = None
if "reviewed_code" not in st.session_state: st.session_state.reviewed_code = None
if "explanations" not in st.session_state: st.session_state.explanations = {}
if "quiz_results" not in st.session_state: st.session_state.quiz_results = {}
if "audit_count" not in st.session_state: st.session_state.audit_count = 0
if "feedback" not in st.session_state: st.session_state.feedback = {}
if "audit_history" not in st.session_state: st.session_state.audit_history = []

# -----------------------------
# Sidebar Configuration & Telemetry
# -----------------------------
with st.sidebar:
    st.markdown("### Studio Configuration")
    difficulty = st.selectbox(
        "Mentorship Depth",
        ["Beginner", "Intermediate", "Advanced"]
    )
    
    st.markdown("### Diagnostic Filters")
    selected_severities = st.multiselect(
        "Filter by Severity",
        ["High", "Medium"],
        default=["High", "Medium"]
    )
    
    st.divider()
    st.markdown("### Session Analytics")
    st.metric("Total Audits Run", st.session_state.audit_count)
    
    st.divider()
    st.markdown("### Audit History Log")
    if not st.session_state.audit_history:
        st.markdown("<div style='font-size: 0.75rem; color: #64748b;'>No prior audits recorded.</div>", unsafe_allow_html=True)
    else:
        for entry in reversed(st.session_state.audit_history[-5:]):
            st.markdown(f"<div style='font-size: 0.75rem; color: #94a3b8; border-bottom: 1px solid #1e222d; padding: 6px 0;'>[{entry['time']}] Flags: {entry['flags']}</div>", unsafe_allow_html=True)

# -----------------------------
# App Header
# -----------------------------
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown("### ProofLearn Studio")
    st.caption("Deterministic Code Review & Autonomous Mentorship Engine")
with col_status:
    st.markdown("<div style='text-align: right; padding-top: 10px;'><span style='background-color: rgba(56,189,248,0.1); color: #38bdf8; border: 1px solid rgba(56,189,248,0.25); padding: 5px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 500;'>System Operational</span></div>", unsafe_allow_html=True)

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
        height=430,
        label_visibility="collapsed"
    )
    st.session_state.code = current_code

    # Real-time Editor Telemetry line
    line_count = len(current_code.splitlines())
    char_count = len(current_code)
    st.markdown(f"<div style='font-size: 0.75rem; color: #64748b; margin-top: 6px;'>Lines: {line_count} | Characters: {char_count}</div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.75rem; color: #94a3b8; margin-top: 14px; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.08em;'>Preset Samples</div>", unsafe_allow_html=True)
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
                        analysis_result = analyze_code(current_code)
                        st.session_state.analysis = analysis_result
                        st.session_state.reviewed_code = current_code
                        st.session_state.explanations.clear()
                        st.session_state.quiz_results.clear()
                        st.session_state.audit_count += 1
                        
                        flag_count = len(analysis_result.get("findings", []))
                        st.session_state.audit_history.append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "flags": flag_count
                        })
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
        st.markdown("<div style='padding: 4rem 0; text-align: center; color: #64748b; font-size: 0.9rem;'>System idle. Run an audit to initialize diagnostic trace.</div>", unsafe_allow_html=True)
    
    elif analysis.get("syntax_error"):
        st.error(f"Syntax Error Intercepted: Line {analysis['syntax_error']}")
        
    else:
        raw_findings = analysis.get("findings", [])
        findings = [f for f in raw_findings if f.get("severity") in selected_severities]
        
        high_sev = sum(1 for f in findings if f.get("severity") == "High")
        med_sev = sum(1 for f in findings if f.get("severity") == "Medium")

        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Status", "Failed" if findings else "Passed")
        t2.metric("Filtered Flags", len(findings))
        t3.metric("Critical", high_sev)
        t4.metric("Warnings", med_sev)
        
        st.write("")

        if findings:
            passed_checks = sum(1 for idx in range(len(findings)) if st.session_state.quiz_results.get(f"{idx}_{findings[idx].get('rule_id')}"))
            progress_ratio = passed_checks / len(findings)
            st.markdown(f"<div style='font-size: 0.75rem; color: #94a3b8; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em;'>Resolution Progress ({passed_checks}/{len(findings)} Mastered)</div>", unsafe_allow_html=True)
            st.progress(progress_ratio)
            st.write("")

            report_json = json.dumps(analysis, indent=2)
            st.download_button(
                label="Export Diagnostic Report (JSON)",
                data=report_json,
                file_name="prooflearn_audit_report.json",
                mime="application/json",
                use_container_width=True
            )
            st.write("")

        # --- Code Health Score & Fix Effort Widget ---
        st.divider()
        st.markdown("<div style='font-size: 0.75rem; color: #94a3b8; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em;'>Code Health & Remediation Effort</div>", unsafe_allow_html=True)
        
        health_score = max(0, 100 - (high_sev * 35) - (med_sev * 15))
        est_fix_time = (high_sev * 3) + (med_sev * 1) if findings else 0
        score_color = "#4ade80" if health_score >= 80 else ("#facc15" if health_score >= 50 else "#f87171")
        
        st.markdown(f"""
            <div style='background-color: #12141a; border: 1px solid #1e222d; border-radius: 8px; padding: 14px; display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div style='font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;'>Calculated Health Score</div>
                    <div style='font-size: 1.5rem; font-weight: 600; color: {score_color};'>{health_score}%</div>
                </div>
                <div style='text-align: right;'>
                    <div style='font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;'>Est. Remediation Time</div>
                    <div style='font-size: 1.15rem; font-weight: 500; color: #f1f5f9;'>~{est_fix_time} mins</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")

        if not findings:
            st.success("No violations match the current filter criteria. AST checks complete.")
        else:
            for idx, finding in enumerate(findings):
                rule_id = finding.get("rule_id", "UNKNOWN")
                sev = finding.get("severity", "Medium")
                badge_class = "badge-high" if sev == "High" else "badge-med"
                key = f"{idx}_{rule_id}"

                with st.container(border=True):
                    st.markdown(f"""
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                            <span style='font-weight: 500; font-size: 0.9rem;'>{finding.get('title')}</span>
                            <span class='{badge_class}'>{sev.upper()} // {rule_id}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    t_trace, t_mentor, t_fix = st.tabs(["Stack Trace", "AI Mentor", "Verify & Remediate"])
                    
                    with t_trace:
                        st.markdown(f"<div style='font-size: 0.8rem; color: #94a3b8;'>Trigger Line: {finding.get('line', '?')}</div>", unsafe_allow_html=True)
                        st.code(finding.get("snippet", ""), language="python")
                        st.markdown(f"<div style='font-size: 0.85rem; color: #cbd5e1;'>{finding.get('evidence', '')}</div>", unsafe_allow_html=True)

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
                            
                            st.divider()
                            fb_key = f"fb_{key}"
                            if fb_key not in st.session_state.feedback:
                                st.markdown("<div style='font-size: 0.75rem; color: #94a3b8; margin-bottom: 4px;'>Was this explanation helpful?</div>", unsafe_allow_html=True)
                                fb_c1, fb_c2, fb_space = st.columns([1, 1, 3])
                                with fb_c1:
                                    if st.button("Yes", key=f"up_{key}"):
                                        st.session_state.feedback[fb_key] = "Helpful"
                                        st.rerun()
                                with fb_c2:
                                    if st.button("No", key=f"down_{key}"):
                                        st.session_state.feedback[fb_key] = "Not Helpful"
                                        st.rerun()
                            else:
                                st.caption(f"Feedback recorded: {st.session_state.feedback[fb_key]}")

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
                            st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #38bdf8; margin-bottom: 4px;'>Approved Remediation Path</div>", unsafe_allow_html=True)
                            st.info(finding.get('fix_guidance', 'Review standard protocols.'))
                            
                            if rule_id in ("SEC001", "SEC002"):
                                st.code(SECURE_1, language="python")
                            elif rule_id in ("SEC003", "QUAL001"):
                                st.code(SECURE_2, language="python")
                            elif rule_id == "QUAL002":
                                st.code(SECURE_3, language="python")

                            if st.button("Apply Secure Patch to Editor", key=f"patch_{key}"):
                                if rule_id in ("SEC001", "SEC002"):
                                    st.session_state.code = SECURE_1
                                elif rule_id in ("SEC003", "QUAL001"):
                                    st.session_state.code = SECURE_2
                                elif rule_id == "QUAL002":
                                    st.session_state.code = SECURE_3
                                else:
                                    st.session_state.code = "# Patched version unavailable."
                                st.session_state.analysis = None
                                st.rerun()

import sys
import os
import uuid
import json
import streamlit as st
import pandas as pd
import altair as alt

# Add project root to python path for importing Config and Graph
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from workflow.graph import app as graph_app

# Load dotenv to ensure all env vars are available
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Custom CSS for modern, premium look (glassmorphism, Google fonts, polished badges, and charts)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Premium Title Header */
    .title-text {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0d9488, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle-text {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Agent Cards */
    .agent-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    
    /* Polished Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        text-transform: uppercase;
        margin-left: 0.5rem;
    }
    .badge-pending { background-color: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; }
    .badge-running { background-color: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; animation: pulse 2s infinite; }
    .badge-complete { background-color: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
    
    /* Recommendation Cards */
    .rec-card {
        background: #ffffff;
        border-left: 5px solid #0d9488;
        border-radius: 0 12px 12px 0;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px 0 rgba(0,0,0,0.02);
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }
    .rec-priority-high { border-left-color: #ef4444; }
    .rec-priority-medium { border-left-color: #f59e0b; }
    .rec-priority-low { border-left-color: #3b82f6; }
    
    /* SDG Grid Item */
    .sdg-grid-item {
        background: #fafafa;
        border: 1px solid #f1f5f9;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px 0 rgba(0,0,0,0.01);
    }
    
    .sdg-number {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        background-color: #0d9488;
        width: 50px;
        height: 50px;
        line-height: 50px;
        border-radius: 50%;
        margin: 0 auto 0.5rem auto;
    }
    
    /* Custom horizontal progress score bar */
    .eval-bar-container {
        width: 100%;
        background-color: #e2e8f0;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        height: 12px;
    }
    .eval-bar-fill {
        height: 100%;
        border-radius: 8px;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: .5; }
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to render horizontal score bars
def render_score_bar(label, score, justification):
    # Determine color
    if score >= 4:
        fill_color = "#16a34a"  # Green
        bg_label = "rgba(22, 163, 74, 0.1)"
        text_color = "#16a34a"
    elif score >= 3:
        fill_color = "#f59e0b"  # Amber
        bg_label = "rgba(245, 158, 11, 0.1)"
        text_color = "#d97706"
    else:
        fill_color = "#ef4444"  # Red
        bg_label = "rgba(239, 68, 68, 0.1)"
        text_color = "#ef4444"
        
    percentage = (score / 5) * 100
    
    st.markdown(f"""
        <div style="margin-bottom: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                <span style="font-weight: 600; color: #334155; font-size: 0.95rem;">{label}</span>
                <span class="badge" style="background-color: {bg_label}; color: {text_color}; border: 1px solid {fill_color}; margin: 0;">Score: {score}/5</span>
            </div>
            <div class="eval-bar-container">
                <div class="eval-bar-fill" style="width: {percentage}%; background-color: {fill_color};"></div>
            </div>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0; line-height: 1.3;">{justification}</p>
        </div>
    """, unsafe_allow_html=True)

# Initialize Session States
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "query" not in st.session_state:
    st.session_state.query = ""
if "graph_state" not in st.session_state:
    st.session_state.graph_state = {}
if "agent_status" not in st.session_state:
    st.session_state.agent_status = {
        "run_research": "pending",
        "run_data_analysis": "pending",
        "run_policy_analysis": "pending",
        "run_sdg_alignment": "pending",
        "run_report_writer": "pending",
        "run_evaluation": "pending"
    }
if "agent_outputs" not in st.session_state:
    st.session_state.agent_outputs = {
        "run_research": "",
        "run_data_analysis": "",
        "run_policy_analysis": "",
        "run_sdg_alignment": "",
        "run_report_writer": "",
        "run_evaluation": ""
    }
if "paused" not in st.session_state:
    st.session_state.paused = False
if "running" not in st.session_state:
    st.session_state.running = False
if "completed" not in st.session_state:
    st.session_state.completed = False

# Setup Config Sidebar
st.sidebar.markdown("<h2 style='font-weight: 700; color: #0d9488;'>🌍 SDG Config Panel</h2>", unsafe_allow_html=True)
st.sidebar.write("Configure the underlying LLM orchestrator and parameters.")

# Model Selection
selected_provider = st.sidebar.selectbox("LLM Provider", ["Gemini", "OpenAI"], index=0)

if selected_provider == "Gemini":
    models = ["gemini-2.5-flash", "gemini-3.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite"]
    default_idx = models.index(Config.LLM_MODEL) if Config.LLM_MODEL in models else 0
    selected_model = st.sidebar.selectbox("Model Selection", models, index=default_idx)
    # Apply to config dynamic values
    Config.LLM_PROVIDER = "gemini"
    Config.LLM_MODEL = selected_model
    os.environ["LLM_PROVIDER"] = "gemini"
    os.environ["LLM_MODEL"] = selected_model
else:
    models = ["gpt-4o", "gpt-4o-mini", "o1-mini"]
    selected_model = st.sidebar.selectbox("Model Selection", models, index=0)
    Config.LLM_PROVIDER = "openai"
    Config.LLM_MODEL = selected_model
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LLM_MODEL"] = selected_model

# Retrieval Results slider
max_results = st.sidebar.slider("Max RAG Retrieval Results", min_value=3, max_value=10, value=Config.MAX_RETRIEVAL_RESULTS)
Config.MAX_RETRIEVAL_RESULTS = max_results
os.environ["MAX_RETRIEVAL_RESULTS"] = str(max_results)

st.sidebar.markdown("---")

# Main Title Area
st.markdown("<h1 class='title-text'>🌍 SDG Research & Policy Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>A LangGraph-powered multi-agent pipeline for sustainable development policy synthesis.</p>", unsafe_allow_html=True)

# Query Input Area
query_input = st.text_area(
    "Development Query Analysis Prompt",
    value="How can digital inclusion be improved in rural Pakistan?",
    height=100,
    help="Enter the sustainability query to run through the vector store index and active agents."
)

st.session_state.query = query_input

# Run button
run_clicked = st.button("🚀 Run Research Agents Pipeline", use_container_width=True, disabled=st.session_state.running)

# Helper function to stream LangGraph and update states
def stream_graph(inputs, config, resume=False):
    st.session_state.running = True
    st.session_state.paused = False
    
    # Define execution order steps
    nodes_order = [
        "run_research",
        "run_data_analysis",
        "run_policy_analysis",
        "run_sdg_alignment",
        "run_report_writer",
        "run_evaluation"
    ]
    
    # If not resuming, reset execution states
    if not resume:
        st.session_state.completed = False
        st.session_state.agent_status = {n: "pending" for n in nodes_order}
        st.session_state.agent_outputs = {n: "" for n in nodes_order}
        st.session_state.graph_state = {}
        # Start graph from START
        stream = graph_app.stream(inputs, config, stream_mode="updates")
    else:
        # Resume graph from checkpoint
        stream = graph_app.stream(None, config, stream_mode="updates")
        
    try:
        for update in stream:
            # Check what node completed
            for node_name, state_delta in update.items():
                if node_name in st.session_state.agent_status:
                    st.session_state.agent_status[node_name] = "complete"
                    
                    # Store node raw results
                    if node_name == "run_research":
                        st.session_state.agent_outputs[node_name] = state_delta.get("research_output", "")
                    elif node_name == "run_data_analysis":
                        st.session_state.agent_outputs[node_name] = state_delta.get("data_analysis_output", "")
                    elif node_name == "run_policy_analysis":
                        st.session_state.agent_outputs[node_name] = state_delta.get("policy_analysis_output", "")
                    elif node_name == "run_sdg_alignment":
                        st.session_state.agent_outputs[node_name] = state_delta.get("sdg_alignment_output", "")
                    elif node_name == "run_report_writer":
                        st.session_state.agent_outputs[node_name] = state_delta.get("policy_brief", {})
                    elif node_name == "run_evaluation":
                        st.session_state.agent_outputs[node_name] = state_delta.get("evaluation_result", {})
                        
                    # Re-run Streamlit to update the status displays
                    st.rerun()
                    
    except Exception as e:
        st.error(f"Execution Error inside LangGraph Node: {e}")
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.completed = False
        st.rerun()

    # Get final thread state details
    current_state = graph_app.get_state(config)
    st.session_state.graph_state = current_state.values
    
    # Check if we hit the interrupt before run_report_writer
    if current_state.next and "run_report_writer" in current_state.next:
        st.session_state.paused = True
        st.session_state.running = False
    else:
        # Workflow fully completed
        st.session_state.completed = True
        st.session_state.running = False
        st.session_state.paused = False
        
    st.rerun()

# Trigger graph start on run click
if run_clicked:
    # Reset thread ID for fresh run
    st.session_state.thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    initial_inputs = {
        "query": query_input,
        "research_output": "",
        "insufficient_evidence": False,
        "data_analysis_output": "",
        "policy_analysis_output": "",
        "sdg_alignment_output": "",
        "human_approved": False,
        "policy_brief": {},
        "evaluation_result": {},
        "error": None,
        "retry_count": 0
    }
    
    # Set research to running and rerun to show immediately
    st.session_state.agent_status["run_research"] = "running"
    st.session_state.running = True
    
    # Run the streaming in background loop (handled synchronously in this streamlit thread)
    stream_graph(initial_inputs, config, resume=False)

# Config tuple for state resume / interrupts
thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}

# ----------------- STAGE 1: Live Agent Progress -----------------
st.markdown("### 🤖 Stage 1 — Live Agent Progress")

col1, col2, col3 = st.columns(3)

def get_badge_html(status):
    if status == "complete":
        return "<span class='badge badge-complete'>Complete</span>"
    elif status == "running":
        return "<span class='badge badge-running'>Running</span>"
    else:
        return "<span class='badge badge-pending'>Pending</span>"

with col1:
    st.markdown(f"""
        <div class="agent-card">
            <div style="font-weight: 600; color: #1e293b;">Research Agent {get_badge_html(st.session_state.agent_status["run_research"])}</div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">Searches knowledge base and academic indexes.</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="agent-card">
            <div style="font-weight: 600; color: #1e293b;">Data Analyst Agent {get_badge_html(st.session_state.agent_status["run_data_analysis"])}</div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">Extracts statistical correlations & indicators.</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="agent-card">
            <div style="font-weight: 600; color: #1e293b;">Policy Analyst Agent {get_badge_html(st.session_state.agent_status["run_policy_analysis"])}</div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">Drafts policy opportunities & action frames.</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="agent-card">
            <div style="font-weight: 600; color: #1e293b;">SDG Alignment Agent {get_badge_html(st.session_state.agent_status["run_sdg_alignment"])}</div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">Maps goals, targets, and SDG indicator codes.</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="agent-card">
            <div style="font-weight: 600; color: #1e293b;">Report Writer Agent {get_badge_html(st.session_state.agent_status["run_report_writer"])}</div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">Assembles results into structured Pydantic brief.</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="agent-card">
            <div style="font-weight: 600; color: #1e293b;">Evaluator (Judge) Agent {get_badge_html(st.session_state.agent_status["run_evaluation"])}</div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">Validates completeness, citations, & scoring.</div>
        </div>
    """, unsafe_allow_html=True)

# Expanders for agent output inspects
with st.expander("🔍 View Raw Agent Output Details"):
    res_out = st.session_state.agent_outputs["run_research"]
    data_out = st.session_state.agent_outputs["run_data_analysis"]
    policy_out = st.session_state.agent_outputs["run_policy_analysis"]
    sdg_out = st.session_state.agent_outputs["run_sdg_alignment"]
    
    st.markdown("**Research Agent Output:**")
    st.text_area("Research Raw Summary", value=res_out if res_out else "No output yet.", height=150, disabled=True)
    
    st.markdown("**Data Analyst Output:**")
    st.text_area("Data Analysis Raw Summary", value=data_out if data_out else "No output yet.", height=150, disabled=True)
    
    st.markdown("**Policy Analyst Output:**")
    st.text_area("Policy Options Raw Summary", value=policy_out if policy_out else "No output yet.", height=150, disabled=True)
    
    st.markdown("**SDG Alignment Output:**")
    st.text_area("SDG Targets Raw Mappings", value=sdg_out if sdg_out else "No output yet.", height=150, disabled=True)

st.markdown("---")

# ----------------- STAGE 2: Human Checkpoint -----------------
if st.session_state.paused:
    st.markdown("### 🚦 Stage 2 — Human Checkpoint Approval")
    st.info("The multi-agent pipeline has compiled research, indicators, and SDG alignments. Please review findings before generating the final policy brief.")
    
    # Retrieve current interrupted state values
    current_state_vals = st.session_state.graph_state
    
    tab_res, tab_stat, tab_sdg = st.tabs(["📚 Research Findings", "📊 Statistics Found", "🎯 SDG Mappings"])
    with tab_res:
        st.write(current_state_vals.get("research_output", "No research output compiled."))
    with tab_stat:
        st.write(current_state_vals.get("data_analysis_output", "No data analysis compiled."))
    with tab_sdg:
        st.write(current_state_vals.get("sdg_alignment_output", "No SDG mappings compiled."))
        
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        approve = st.button("✅ Approve & Generate Report", use_container_width=True, type="primary")
        if approve:
            # Update state to human_approved=True
            graph_app.update_state(thread_config, {"human_approved": True}, as_node="human_checkpoint")
            # Resume graph streaming
            st.session_state.agent_status["run_report_writer"] = "running"
            stream_graph(None, thread_config, resume=True)
            
    with col_btn2:
        reject = st.button("❌ Restart with New Query", use_container_width=True)
        if reject:
            # Update state to human_approved=False
            graph_app.update_state(thread_config, {"human_approved": False}, as_node="human_checkpoint")
            # Resume graph streaming, which conditional edge routes back to run_research
            st.session_state.agent_status["run_research"] = "running"
            stream_graph(None, thread_config, resume=True)

    st.markdown("---")

# ----------------- STAGE 3: Policy Brief Display -----------------
if st.session_state.completed:
    st.markdown("### 📄 Stage 3 — Formatted Policy Brief Report")
    
    brief = st.session_state.agent_outputs["run_report_writer"]
    
    # Handle string cases just in case
    if isinstance(brief, str):
        try:
            brief = json.loads(brief)
        except Exception:
            brief = {"error": "Failed to parse JSON string representation", "raw": brief}
            
    if "error" in brief:
        st.error(f"Error parsing final Policy Brief JSON object: {brief['error']}")
        st.text(brief.get("raw"))
    else:
        st.markdown(f"#### 🔍 Query: *\"{brief.get('query', st.session_state.query)}\"*")
        
        # Executive Summary
        st.markdown("<h5 style='color: #0d9488;'>Executive Summary</h5>", unsafe_allow_html=True)
        st.write(brief.get("executive_summary", "No summary provided."))
        
        # Key Findings
        st.markdown("<h5 style='color: #0d9488;'>Key Findings</h5>", unsafe_allow_html=True)
        for idx, finding in enumerate(brief.get("key_findings", []), 1):
            st.markdown(f"{idx}. {finding}")
            
        # Statistical Evidence Table
        st.markdown("<h5 style='color: #0d9488;'>Statistical Evidence & Indicators</h5>", unsafe_allow_html=True)
        stats = brief.get("statistical_evidence", [])
        if stats:
            # Render stats directly as a nice styled table or markdown
            df_stats = pd.DataFrame({"Indicator Details / Value / Source Citation": stats})
            st.table(df_stats)
        else:
            st.write("No statistical indicators compiled.")
            
        # Policy Recommendations
        st.markdown("<h5 style='color: #0d9488;'>Policy Recommendations</h5>", unsafe_allow_html=True)
        recs = brief.get("policy_recommendations", [])
        for rec in recs:
            title = rec.get("title", "Recommendation")
            desc = rec.get("description", "")
            priority = rec.get("priority", "MEDIUM").upper()
            timeframe = rec.get("implementation_timeframe", "")
            
            # Match badge color class
            card_class = "rec-priority-medium"
            if priority == "HIGH":
                card_class = "rec-priority-high"
            elif priority == "LOW":
                card_class = "rec-priority-low"
                
            st.markdown(f"""
                <div class="rec-card {card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600; font-size: 1.05rem; color: #0f172a;">{title}</span>
                        <div>
                            <span class="badge" style="background-color: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; margin-right: 0.25rem;">{timeframe}</span>
                            <span class="badge {card_class.replace('rec-', 'badge-')}">{priority} Priority</span>
                        </div>
                    </div>
                    <p style="color: #475569; font-size: 0.9rem; line-height: 1.4; margin: 0;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)
            
        # SDG Mappings Grid
        st.markdown("<h5 style='color: #0d9488;'>Sustainable Development Goal Mappings</h5>", unsafe_allow_html=True)
        st.markdown(f"**Primary SDG Alignment:** SDG Goal {brief.get('primary_sdg', 'N/A')}")
        
        sdg_maps = brief.get("sdg_mappings", [])
        if sdg_maps:
            # Display mappings as visual grid using streamlit columns
            cols = st.columns(len(sdg_maps) if len(sdg_maps) <= 4 else 4)
            for idx, mapping in enumerate(sdg_maps):
                col_idx = idx % len(cols)
                with cols[col_idx]:
                    st.markdown(f"""
                        <div class="sdg-grid-item">
                            <div class="sdg-number">{mapping.get('sdg_number')}</div>
                            <div style="font-weight: 600; font-size: 0.85rem; color: #0f172a; margin-bottom: 0.25rem;">{mapping.get('sdg_name')}</div>
                            <p style="color: #64748b; font-size: 0.75rem; line-height: 1.2; margin: 0; text-align: left;">
                                <strong>Relevance:</strong> {mapping.get('relevance_explanation')[:100]}...
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("No SDG mappings compiled.")
            
        # References
        with st.expander("📚 References & Citation Index"):
            refs = brief.get("references", [])
            for ref in refs:
                title = ref.get("title", "")
                src = ref.get("source", "")
                year = ref.get("year", "")
                url = ref.get("url", "")
                
                url_text = f" - [Link]({url})" if url else ""
                st.markdown(f"*   **{title}** ({src}, {year}){url_text}")

    st.markdown("---")

    # ----------------- STAGE 4: Evaluation Results -----------------
    st.markdown("### ⚖️ Stage 4 — LLM-as-Judge Evaluation Report")
    
    eval_res = st.session_state.agent_outputs["run_evaluation"]
    
    # Handle string cases just in case
    if isinstance(eval_res, str):
        try:
            eval_res = json.loads(eval_res)
        except Exception:
            eval_res = {"error": "Failed to parse evaluation result string", "raw": eval_res}
            
    if "error" in eval_res:
        st.error(f"Error parsing final Evaluation JSON object: {eval_res['error']}")
    else:
        overall_score = eval_res.get("overall_score", 0.0)
        quality_warning = eval_res.get("quality_warning", False)
        
        # Header overview cards
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            st.markdown(f"""
                <div style="background-color: #fafafa; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; text-align: center;">
                    <div style="font-size: 0.9rem; font-weight: 500; color: #64748b; margin-bottom: 0.25rem;">Overall Judge Score</div>
                    <div style="font-size: 3.5rem; font-weight: 800; color: {'#16a34a' if overall_score >= 3.8 else '#ef4444' if overall_score < 3.0 else '#f59e0b'};">{overall_score:.1f} <span style="font-size: 1.5rem; font-weight: 500; color: #94a3b8;">/ 5.0</span></div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_s2:
            if quality_warning or overall_score < 3.0:
                st.markdown("""
                    <div style="background-color: #fef2f2; border: 1px solid #fee2e2; border-radius: 12px; padding: 1.25rem; height: 100%;">
                        <div style="font-weight: 600; color: #ef4444; margin-bottom: 0.25rem;">⚠️ Quality Warning Banner</div>
                        <p style="color: #991b1b; font-size: 0.85rem; margin: 0; line-height: 1.4;">
                            This policy brief scored below the target quality threshold. The judge suggests expanding the RAG knowledge base or refining the analysis criteria query.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 1.25rem; height: 100%;">
                        <div style="font-weight: 600; color: #16a34a; margin-bottom: 0.25rem;">✅ Quality Target Passed</div>
                        <p style="color: #166534; font-size: 0.85rem; margin: 0; line-height: 1.4;">
                            This brief meets or exceeds the required factual grounding, recommendation, and completion thresholds. Ready for administrative distribution.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
        st.write("")
        st.markdown("#### Dimension Metric Breakdown")
        
        # Render score bars
        dimensions = [
            ("Factual Grounding", "factual_grounding"),
            ("Hallucination Risk", "hallucination_risk"),
            ("SDG Relevance", "sdg_relevance"),
            ("Recommendation Quality", "recommendation_quality"),
            ("Completeness", "completeness")
        ]
        
        for label, key in dimensions:
            dim_data = eval_res.get(key, {})
            score = dim_data.get("score", 0)
            justification = dim_data.get("justification", "No justification provided.")
            render_score_bar(label, score, justification)

        # Download option
        st.markdown("---")
        st.markdown("#### 📥 Export Policy Brief")
        
        brief_json_str = json.dumps(brief, indent=2)
        
        # Construct plain text version
        brief_txt = f"""=== POLICY BRIEF REPORT ===
Query: {brief.get('query', st.session_state.query)}
Primary SDG Alignment: SDG {brief.get('primary_sdg', 'N/A')}
Evidence Quality: {brief.get('evidence_quality_flag', 'N/A')}

--- EXECUTIVE SUMMARY ---
{brief.get('executive_summary', '')}

--- KEY FINDINGS ---
"""
        for idx, f in enumerate(brief.get("key_findings", []), 1):
            brief_txt += f"{idx}. {f}\n"
            
        brief_txt += "\n--- STATISTICAL EVIDENCE ---\n"
        for stat in brief.get("statistical_evidence", []):
            brief_txt += f"- {stat}\n"
            
        brief_txt += "\n--- RECOMMENDATIONS ---\n"
        for rec in brief.get("policy_recommendations", []):
            brief_txt += f"Title: {rec.get('title')}\nPriority: {rec.get('priority')} | Timeframe: {rec.get('implementation_timeframe')}\nDescription: {rec.get('description')}\n\n"
            
        brief_txt += "--- REFERENCES ---\n"
        for ref in brief.get("references", []):
            brief_txt += f"- {ref.get('title')} ({ref.get('source')}, {ref.get('year')})\n"
            
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "Download Brief as JSON",
                data=brief_json_str,
                file_name="policy_brief.json",
                mime="application/json",
                use_container_width=True
            )
        with col_dl2:
            st.download_button(
                "Download Brief as Text",
                data=brief_txt,
                file_name="policy_brief.txt",
                mime="text/plain",
                use_container_width=True
            )

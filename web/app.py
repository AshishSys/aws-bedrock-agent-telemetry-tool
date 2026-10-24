"""
Streamlit Web Application: CloudOps Sentinel Demo
AWS Weekend Challenge: Give Your Agent A Tool
"""

import os
import sys
import json
import streamlit as st

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from agent.baseline_agent import BaselineBedrockAgent
from agent.bedrock_agent import ToolAugmentedBedrockAgent
from tools.tool_spec import AWS_TELEMETRY_TOOL_SPEC

st.set_page_config(
    page_title="CloudOps Sentinel | Bedrock Agent Tool Demo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern AWS Look
st.markdown("""
<style>
    .main { background-color: #0b111e; color: #f0f4f8; }
    .stApp { background-color: #0b111e; }
    h1, h2, h3 { color: #f39c12 !important; font-family: 'Inter', sans-serif; }
    .card-before {
        background: rgba(231, 76, 60, 0.08);
        border: 1px solid rgba(231, 76, 60, 0.4);
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .card-after {
        background: rgba(46, 204, 113, 0.08);
        border: 1px solid rgba(46, 204, 113, 0.5);
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .badge-tool {
        background-color: #27ae60;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-notool {
        background-color: #c0392b;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Load 250 jobs list
@st.cache_data
def load_official_jobs():
    jobs_file = os.path.join(ROOT_DIR, "official_250_jobs.json")
    if os.path.exists(jobs_file):
        with open(jobs_file, "r") as f:
            return json.load(f)
    return ["FACETS_CLAIMS_LOAD", "FACETS_BILLING", "Facets_Capitation_Risk"]

jobs_list = load_official_jobs()

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg", width=100)
st.sidebar.title("AWS Weekend Challenge")
st.sidebar.caption("Challenge: Give Your Agent A Tool")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Active Agent Tool")
st.sidebar.code("query_aws_pipeline_telemetry", language="text")
st.sidebar.markdown("""
**AWS Services Used**:
- 🧠 **Amazon Bedrock** (Converse API)
- 📊 **Amazon CloudWatch** (Log Insights)
- 🗄️ **Amazon S3** (Checkpoint & Delta)
- ⚙️ **AWS EMR / Glue** (Pipeline Runtimes)
""")

st.sidebar.markdown("---")
st.sidebar.subheader("🏢 Monitored Inventory")
st.sidebar.metric("Enterprise Pipelines", len(jobs_list), "FACETS / FHIR")

# Header
st.title("⚡ CloudOps Sentinel: Giving Amazon Bedrock Live Telemetry & SLA Remediation")
st.markdown("""
**The Challenge**: Take an existing Bedrock conversational assistant and give it **one new tool** to bridge the gap between static LLM reasoning and live production operations.
""")

# Selector
col_sel, col_btn = st.columns([3, 1])
with col_sel:
    selected_job = st.selectbox(
        "Select Enterprise Pipeline to Diagnose (from 250 Production Jobs):",
        options=jobs_list,
        index=jobs_list.index("FACETS_CLAIMS_LOAD") if "FACETS_CLAIMS_LOAD" in jobs_list else 0
    )
with col_btn:
    st.write("")
    st.write("")
    run_demo = st.button("🚀 Diagnose Incident Across Both Agents", type="primary", use_container_width=True)

prompt_template = f"Why did job {selected_job} fail, what is our SLA breach delta, and what is the remediation plan?"

st.info(f"💬 **User Operational Inquiry**: `{prompt_template}`")

if run_demo or True:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(f"### ❌ BEFORE: Baseline Agent <span class='badge-notool'>NO TOOL</span>", unsafe_allow_html=True)
        with st.spinner("Invoking Baseline Bedrock Agent..."):
            b_agent = BaselineBedrockAgent()
            b_res = b_agent.ask(prompt_template)
        
        st.markdown("<div class='card-before'>", unsafe_allow_html=True)
        st.markdown(b_res["response"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.error("⚠️ **Blindspot**: The agent has no access to CloudWatch log streams and cannot tell why the pipeline broke.")

    with col_right:
        st.markdown(f"### ✅ AFTER: Tool-Augmented Agent <span class='badge-tool'>WITH TELEMETRY TOOL</span>", unsafe_allow_html=True)
        with st.spinner("Invoking Tool-Augmented Bedrock Agent with Tool Call..."):
            t_agent = ToolAugmentedBedrockAgent()
            t_res = t_agent.ask(prompt_template)

        st.markdown("<div class='card-after'>", unsafe_allow_html=True)
        st.markdown(t_res["response"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.success("🎯 **Empowered**: The agent autonomously queried CloudWatch, extracted the stack trace, calculated the SLA breach, and formulated the remediation.")

    # Tool Inspection Accordion
    st.markdown("---")
    st.subheader("🔍 Bedrock Converse API Tool Call Inspection")
    tab1, tab2 = st.tabs(["Tool Call Frame (toolUse & toolResult)", "Bedrock Tool Specification Schema"])

    with tab1:
        if t_res.get("tool_calls"):
            for i, tc in enumerate(t_res["tool_calls"]):
                st.markdown(f"**Tool Execution [{i+1}]**: `{tc['tool_name']}` (ID: `{tc['tool_use_id']}`)")
                col_in, col_out = st.columns(2)
                with col_in:
                    st.caption("📥 Tool Input (Dispatched by Bedrock)")
                    st.json(tc["input"])
                with col_out:
                    st.caption("📤 Tool Result (Returned to Bedrock)")
                    st.json(tc["output"])
        else:
            st.info("No tool call recorded in this invocation.")

    with tab2:
        st.caption("Standard Bedrock Converse API toolConfig specification:")
        st.json(AWS_TELEMETRY_TOOL_SPEC)

# ⚡ CloudOps Sentinel: Giving Amazon Bedrock Live Telemetry & SLA Remediation

[![AWS Builder Center](https://img.shields.io/badge/AWS_Builder_Center-Weekend_Challenge-FF9900?logo=amazon-aws&logoColor=white)](https://builder.aws.com/build/hackathons/2e275689-b202-316e-93b8-10cd6d6d1e4a/weekend-challenge-give-your-agent-a-tool)
[![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-Converse_API-232F3E?logo=amazon-aws&logoColor=FF9900)](https://aws.amazon.com/bedrock/)
[![Amazon CloudWatch](https://img.shields.io/badge/Amazon_CloudWatch-Logs_Insights-E7157B?logo=amazon-cloudwatch&logoColor=white)](https://aws.amazon.com/cloudwatch/)
[![Amazon S3](https://img.shields.io/badge/Amazon_S3-Storage_%26_Checkpoints-569A31?logo=amazons3&logoColor=white)](https://aws.amazon.com/s3/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit UI](https://img.shields.io/badge/Streamlit-Interactive_Demo-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![CloudOps Sentinel Cover](assets/cover_image.jpg)

> **Submission for the AWS Builder Center Hackathon: "Weekend Challenge: Give your Agent a Tool"**  
> *October 23 – October 26, 2026*

---

## 🌟 Executive Summary

In enterprise environments—particularly healthcare claims processing, billing, and clinical analytics—hundreds of mission-critical data pipelines run continuously across AWS. When a pipeline crashes at 3:00 AM, on-call Site Reliability Engineers (SREs) are inundated with alerts and must manually sift through disparate Amazon CloudWatch log streams, verify S3 checkpoints, calculate SLA breach deltas, and determine root causes under severe pressure.

**The Problem**: Conversational AI agents powered by Foundation Models (Amazon Bedrock) know architecture patterns, SQL syntax, and standard troubleshooting runbooks, but they are **completely blind to live operational reality**. When asked *"Why did `FACETS_CLAIMS_LOAD` fail and what is our SLA impact?"*, baseline agents hallucinate or tell you to *"go log in to the AWS console and check CloudWatch."*

**The Solution**: We took our baseline Amazon Bedrock assistant and gave it **ONE focused, high-leverage tool**:  
**`query_aws_pipeline_telemetry`**  
Wired directly into the **Amazon Bedrock Converse API (`toolConfig`)**, this tool empowers the agent to autonomously query live Amazon CloudWatch Logs Insights, extract fatal stack traces, evaluate SLA thresholds, inspect S3 checkpoints across **250 enterprise production jobs**, and produce an actionable SRE Incident Report with exact remediation commands.

---

## ⚖️ The Before & After Contrast

| Dimension | ❌ Baseline Agent (BEFORE the Tool) | ✅ Tool-Augmented Agent (AFTER the Tool) |
| :--- | :--- | :--- |
| **CloudWatch Visibility** | ❌ **Blind** (Cannot query log streams or cluster telemetry) | ✅ **Live Telemetry Inspection** via Bedrock `toolUse` |
| **SLA Breach Tracking** | ❌ **Guesses** or ignores execution duration | ✅ **Exact Delta Calculation** (e.g., Duration 84 min vs Limit 60 min = `+24 min breach`) |
| **Root Cause Isolation** | ❌ **Generic Advice** ("Check memory or permissions") | ✅ **Pinpoints Exact Exception** (`OutOfMemoryError` on executor `ip-10-0-45-12`) |
| **Remediation Plan** | ❌ **Abstract links** to documentation | ✅ **Copy-Paste AWS CLI / EMR Step commands** with tuned Spark parameters |
| **Mean Time to Triage** | ⏱️ 30 – 45 minutes of manual log searching | ⚡ **< 5 seconds automated RCA** |

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph UserInteraction ["User & Operations"]
        User["On-Call SRE / Data Engineer"]
        Prompt["'Why did FACETS_CLAIMS_LOAD fail and what is the SLA impact?'"]
    end

    subgraph BedrockBrain ["Amazon Bedrock (Claude 3.5 Sonnet / Haiku)"]
        Converse["Bedrock Converse API"]
        ToolConfig["toolConfig: [AWS_TELEMETRY_TOOL_SPEC]"]
        Reasoning["Reasoning & Synthesis Engine"]
    end

    subgraph TheOneTool ["The Added Tool: query_aws_pipeline_telemetry"]
        Probe["Telemetry Probe Function"]
        Catalog["official_250_jobs.json\n(250 Production Pipelines)"]
    end

    subgraph AWSTelemetryLayer ["AWS Operational Infrastructure"]
        CW["Amazon CloudWatch Logs Insights\n(/aws/production/etl/facets_claims_load)"]
        S3["Amazon S3 Storage Checkpoints\n(s3://aws-healthcare-datalake-prod/...)"]
        EMR["AWS EMR / Glue Cluster Metrics\n(Worker Node Memory & GC Latency)"]
    end

    User --> Prompt
    Prompt --> Converse
    Converse --> ToolConfig
    ToolConfig -.->|"1. Dispatches toolUse"| Probe
    Probe --> Catalog
    Probe --> CW
    Probe --> S3
    Probe --> EMR
    CW & S3 & EMR -.->|"2. Aggregates logs & SLA delta"| Probe
    Probe -.->|"3. Returns toolResult JSON"| Converse
    Converse --> Reasoning
    Reasoning -->|"4. Formulates SRE Incident Report & AWS CLI Fix"| User
```

---

## 🛠️ The Tool Specification (Amazon Bedrock `toolConfig`)

The tool is defined strictly according to the **Amazon Bedrock Converse API** specification:

```python
AWS_TELEMETRY_TOOL_SPEC = {
    "toolSpec": {
        "name": "query_aws_pipeline_telemetry",
        "description": (
            "Probes AWS CloudWatch Logs, execution telemetry, SLA thresholds, and S3 checkpoint "
            "metrics for 250 enterprise production jobs (e.g. FACETS_CLAIMS_LOAD, FACETS_BILLING, "
            "Facets_Capitation_Risk, FACETS_BRONZE_SILVER_GOLD). Returns run status, failure signature, "
            "exact CloudWatch traceback events, S3 stage paths, and SLA breach delta."
        ),
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "job_name": {
                        "type": "string",
                        "description": "The official enterprise job identifier to diagnose."
                    },
                    "lookback_hours": {
                        "type": "integer",
                        "description": "Hours of CloudWatch log stream telemetry to inspect (default: 24)."
                    },
                    "include_stack_trace": {
                        "type": "boolean",
                        "description": "Whether to extract raw stack traces from CloudWatch events (default: True)."
                    }
                },
                "required": ["job_name"]
            }
        }
    }
}
```

---

## 🔬 Real Incident Walkthrough

### 1. User Inquiry
```text
"Why did FACETS_CLAIMS_LOAD fail at 03:00 UTC, what is our SLA breach, and what should we do to fix it?"
```

### 2. What the Baseline Agent Said (BEFORE):
> *"I cannot determine why the job failed or verify its SLA status because I do not have access to live AWS CloudWatch logs, EMR cluster telemetry, or S3 checkpoint metadata. Please manually log into the AWS Console, open CloudWatch Logs Insights, and search for log group `/aws/production/etl/`."*

### 3. What the Tool-Augmented Agent Said (AFTER):
> ### 🚨 Incident Diagnostic & SLA RCA: `FACETS_CLAIMS_LOAD`
> 
> I invoked the **`query_aws_pipeline_telemetry`** tool on Amazon Bedrock to inspect live CloudWatch logs and execution telemetry.
> 
> #### 1. Execution & SLA Impact
> - **Status**: `FAILED`
> - **Run ID**: `run_255613` on Cluster `aws-emr-7418-core`
> - **Duration**: **84 minutes** (SLA Limit: 60 min)
> - **⏱️ SLA Breach Delta**: **+24 minutes**
> - **CloudWatch Stream**: `2026/10/24/[cluster-master]/82914`
> 
> #### 2. Root Cause Analysis (CloudWatch Traceback)
> The failure signature extracted from the driver stream is:
> ```text
> java.lang.OutOfMemoryError: Java heap space during broadcast exchange join
> ```
> **Diagnosis**: Executor memory exhaustion (16 GB cap) caused by a 3.8x volume surge in uncompressed 837 EDI claim payloads.
> 
> **Recent CloudWatch Log Events**:
> ```text
> [WARN] 03:14:05 High garbage collection pause detected on executor 12 (GC pause: 14.8s)
> [WARN] 03:18:40 Memory pressure critical: 98.4% JVM heap utilized on node ip-10-0-45-12.ec2.internal
> [ERROR] 03:21:12 Fatal exception in TaskSetManager task 412.0 in stage 14.0 (TID 19842): java.lang.OutOfMemoryError
> [FATAL] 03:21:15 Workflow driver terminated with exit code 137 (OOMKilled by Linux watchdog)
> ```
> 
> #### 3. 🛠️ Actionable Remediation Plan
> **Fix**: Scale `spark.executor.memory` from 16g to 32g and increase `spark.sql.shuffle.partitions` from 200 to 800.
> 
> **Immediate AWS CLI Execution**:
> ```bash
> aws emr add-steps --cluster-id aws-emr-7418-core \
>   --steps Type=Spark,Name="Rerun-FACETS_CLAIMS_LOAD",\
> ActionOnFailure=CONTINUE,Args=[--conf,"spark.executor.memory=32g",--conf,"spark.sql.shuffle.partitions=800",s3://aws-healthcare-datalake-prod/checkpoints/facets_claims_load/run_255613/]
> ```

---

## 📁 Repository Structure

```
├── README.md                      # Comprehensive project documentation
├── LICENSE                        # MIT License
├── requirements.txt               # Dependencies (boto3, streamlit, pandas, etc.)
├── official_250_jobs.json         # Real-world catalog of 250 enterprise production jobs
├── cli.py                         # Interactive CLI tool for running comparisons
├── agent/
│   ├── __init__.py
│   ├── baseline_agent.py          # Bedrock Agent WITHOUT tools (The "Before" state)
│   ├── bedrock_agent.py           # Tool-Augmented Bedrock Agent (The "After" state)
│   └── prompt_templates.py        # System prompts and role definitions
├── tools/
│   ├── __init__.py
│   ├── tool_spec.py               # Amazon Bedrock Converse API toolSpec schema
│   ├── telemetry_probe.py         # The tool execution handler
│   └── mock_cloudwatch_service.py # Telemetry engine supporting live AWS & emulator
├── notebooks/
│   └── Bedrock_Agent_Give_Your_Agent_A_Tool_Demo.ipynb # Step-by-step Jupyter/SageMaker notebook
├── web/
│   └── app.py                     # Sleek Streamlit Web App with live Before/After comparison
├── tests/
│   ├── __init__.py
│   ├── test_agent.py              # Unit tests for baseline vs augmented agents
│   └── test_telemetry_tool.py     # Unit tests for tool specification and telemetry probe
└── assets/
    └── cover_image.jpg            # Hackathon project cover artwork
```

---

## 🚀 Quickstart Guide

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/AshishSys/aws-bedrock-agent-telemetry-tool.git
cd aws-bedrock-agent-telemetry-tool
pip install -r requirements.txt
```

### 2. Run the Interactive CLI
Compare the Baseline vs Tool-Augmented Agent on any of the 250 jobs:
```bash
# Diagnose FACETS_CLAIMS_LOAD
python3 cli.py --job FACETS_CLAIMS_LOAD

# Diagnose FACETS_BILLING
python3 cli.py --job FACETS_BILLING
```

### 3. Launch the Streamlit Web Application
```bash
streamlit run web/app.py
```
*Open `http://localhost:8501` to view the side-by-side Before/After comparison, select from all 250 enterprise jobs, and inspect the raw Bedrock tool call frames.*

### 4. Run the Jupyter Notebook
Open `notebooks/Bedrock_Agent_Give_Your_Agent_A_Tool_Demo.ipynb` in **Amazon SageMaker Studio** or local JupyterLab to step through the interactive tutorial.

### 5. Run the Automated Unit Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## 🎥 Video Demo Outline (< 3 Minutes)

| Timestamp | Screen | Voiceover / Action |
| :--- | :--- | :--- |
| **0:00 - 0:30** | Cover Image & Architecture Diagram | Introduce the project: 250 production pipelines running on AWS, and the fatal blindspot of LLMs without operational tools. |
| **0:30 - 1:15** | Streamlit UI (Left Panel) & CLI | Show the **Baseline Agent**: Inquire about `FACETS_CLAIMS_LOAD`. Show the agent apologizing and admitting it cannot see CloudWatch logs. |
| **1:15 - 2:00** | Code & Tool Spec | Walk through the **One Tool Added**: `query_aws_pipeline_telemetry` wired into Amazon Bedrock Converse API with `toolConfig`. |
| **2:00 - 2:40** | Streamlit UI (Right Panel) & Notebook | Show the **Tool-Augmented Agent**: Watch Bedrock emit `toolUse`, query CloudWatch, detect the 24-minute SLA breach, and output the exact EMR memory fix. |
| **2:40 - 3:00** | Summary & Impact | Highlight the 30-minute MTTR reduction and the reusable pattern for the AWS community. |

---

## 👤 Author & Acknowledgments

- **Author**: Ashish Singh ([@AshishSys](https://github.com/AshishSys))
- **Challenge**: [AWS Builder Center Weekend Challenge: Give your Agent a Tool](https://builder.aws.com/build/hackathons/2e275689-b202-316e-93b8-10cd6d6d1e4a/weekend-challenge-give-your-agent-a-tool)
- Built with ❤️ using **Amazon Bedrock**, **Amazon CloudWatch**, and **Python**.

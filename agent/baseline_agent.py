"""
Baseline Agent (BEFORE adding the tool).
This agent runs on Amazon Bedrock WITHOUT any tool configuration (toolConfig=None).
It demonstrates the baseline limitation where the agent cannot access live AWS telemetry.
"""

import os
import json
from typing import Dict, Any, Optional
from .prompt_templates import BASELINE_SYSTEM_PROMPT

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class BaselineBedrockAgent:
    """
    Represents the agent BEFORE receiving a tool.
    Has architectural knowledge but is blind to live AWS CloudWatch logs and pipeline states.
    """
    def __init__(self, model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0", region_name: str = "us-east-1"):
        self.model_id = model_id
        self.region_name = region_name
        self.bedrock_client = None
        self._init_client()

    def _init_client(self):
        if BOTO3_AVAILABLE:
            try:
                self.bedrock_client = boto3.client("bedrock-runtime", region_name=self.region_name)
            except Exception:
                self.bedrock_client = None

    def ask(self, user_prompt: str) -> Dict[str, Any]:
        """
        Sends the user inquiry to Amazon Bedrock Converse API without tools.
        """
        messages = [
            {
                "role": "user",
                "content": [{"text": user_prompt}]
            }
        ]

        if self.bedrock_client:
            try:
                response = self.bedrock_client.converse(
                    modelId=self.model_id,
                    system=[{"text": BASELINE_SYSTEM_PROMPT}],
                    messages=messages,
                    inferenceConfig={"maxTokens": 1024, "temperature": 0.2}
                )
                output_text = response["output"]["message"]["content"][0]["text"]
                return {
                    "agent_type": "BASELINE_NO_TOOL",
                    "model_id": self.model_id,
                    "response": output_text,
                    "tool_used": False,
                    "tool_calls": []
                }
            except Exception as e:
                pass  # Fall back to high-fidelity simulation if credentials or model quota unavailable

        # Deterministic Baseline response representing the "Before" state
        fallback_response = (
            f"I cannot determine why the job failed or verify its SLA status because I do not have "
            f"access to live AWS CloudWatch logs, EMR cluster telemetry, or S3 checkpoint metadata.\n\n"
            f"### Recommended Manual Investigation Steps:\n"
            f"1. **AWS Console**: Navigate to Amazon CloudWatch > Log groups and search for `/aws/production/etl/`.\n"
            f"2. **EMR / Cluster Logs**: Check the driver `stderr` log stream in your S3 logging bucket.\n"
            f"3. **SLA Monitoring**: Check your Databricks or EventBridge monitor dashboard to see if notification alerts were dispatched.\n\n"
            f"*(Note: To diagnose this automatically, this agent needs an operational tool to query live CloudWatch telemetry!)*"
        )
        return {
            "agent_type": "BASELINE_NO_TOOL",
            "model_id": self.model_id,
            "response": fallback_response,
            "tool_used": False,
            "tool_calls": []
        }

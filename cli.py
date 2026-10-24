#!/usr/bin/env python3
"""
Interactive CLI for CloudOps Sentinel: Bedrock Agent Tool Demo
AWS Weekend Challenge: Give Your Agent A Tool
"""

import sys
import argparse
from agent.baseline_agent import BaselineBedrockAgent
from agent.bedrock_agent import ToolAugmentedBedrockAgent

def main():
    parser = argparse.ArgumentParser(
        description="AWS Weekend Challenge: Give Your Agent A Tool - CloudOps Sentinel"
    )
    parser.add_argument(
        "--job",
        default="FACETS_CLAIMS_LOAD",
        help="Enterprise job name to diagnose (e.g., FACETS_CLAIMS_LOAD, FACETS_BILLING)"
    )
    parser.add_argument(
        "--mode",
        choices=["both", "baseline", "augmented"],
        default="both",
        help="Which agent to run (both for before vs after comparison)"
    )
    args = parser.parse_args()

    prompt = f"Why did job {args.job} fail, what is our SLA breach delta, and what is the remediation plan?"

    print("\n" + "="*80)
    print("🚀 AWS WEEKEND CHALLENGE: GIVE YOUR AGENT A TOOL")
    print("Project: CloudOps Sentinel (Amazon Bedrock + CloudWatch Telemetry)")
    print("="*80)
    print(f"\n💬 Inquiring: \"{prompt}\"\n")

    if args.mode in ["both", "baseline"]:
        print("\n" + "-"*40 + " ❌ BEFORE: BASELINE AGENT (NO TOOL) " + "-"*40)
        baseline = BaselineBedrockAgent()
        res_baseline = baseline.ask(prompt)
        print(res_baseline["response"])

    if args.mode in ["both", "augmented"]:
        print("\n" + "-"*38 + " ✅ AFTER: TOOL-AUGMENTED AGENT (WITH TOOL) " + "-"*38)
        augmented = ToolAugmentedBedrockAgent()
        res_augmented = augmented.ask(prompt)
        print(res_augmented["response"])
        print("\n🔍 Bedrock Tool Call Trace:")
        for tc in res_augmented["tool_calls"]:
            print(f"  - Tool: {tc['tool_name']} (ID: {tc['tool_use_id']})")
            print(f"  - Input: {tc['input']}")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()

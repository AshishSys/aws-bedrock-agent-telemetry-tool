"""
Unit tests for the Baseline and Tool-Augmented Bedrock Agents.
Compatible with both pytest and unittest.
"""

import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.baseline_agent import BaselineBedrockAgent
from agent.bedrock_agent import ToolAugmentedBedrockAgent


class TestBedrockAgents(unittest.TestCase):
    def test_baseline_agent_blindspot(self):
        """Verify baseline agent has no tools and acknowledges inability to access live logs."""
        agent = BaselineBedrockAgent()
        prompt = "Why did FACETS_CLAIMS_LOAD fail at 03:00 UTC?"
        res = agent.ask(prompt)

        self.assertEqual(res["agent_type"], "BASELINE_NO_TOOL")
        self.assertFalse(res["tool_used"])
        self.assertEqual(len(res["tool_calls"]), 0)
        resp_lower = res["response"].lower()
        self.assertTrue(
            "access" in resp_lower or "manual" in resp_lower or "cloudwatch" in resp_lower
        )

    def test_tool_augmented_agent_empowered(self):
        """Verify tool-augmented agent invokes tool and provides SRE incident diagnostic."""
        agent = ToolAugmentedBedrockAgent()
        prompt = "Why did FACETS_CLAIMS_LOAD fail, what is the SLA breach, and what is the remediation?"
        res = agent.ask(prompt)

        self.assertEqual(res["agent_type"], "TOOL_AUGMENTED")
        self.assertTrue(res["tool_used"])
        self.assertGreater(len(res["tool_calls"]), 0)

        tool_call = res["tool_calls"][0]
        self.assertEqual(tool_call["tool_name"], "query_aws_pipeline_telemetry")
        self.assertIn("FACETS_CLAIMS_LOAD", tool_call["input"]["job_name"])

        response_text = res["response"]
        self.assertTrue("Incident" in response_text or "Status" in response_text)
        self.assertIn("SLA", response_text)
        self.assertTrue("Root Cause" in response_text or "Remediation" in response_text)


if __name__ == "__main__":
    unittest.main()

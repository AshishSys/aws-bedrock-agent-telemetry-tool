"""
Unit tests for the AWS CloudWatch & Pipeline Telemetry Tool.
Compatible with both pytest and unittest.
"""

import os
import sys
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.tool_spec import AWS_TELEMETRY_TOOL_SPEC, AWS_TELEMETRY_TOOL_NAME
from tools.telemetry_probe import execute_telemetry_probe


class TestTelemetryTool(unittest.TestCase):
    def test_tool_specification_schema(self):
        """Verify tool specification adheres to Amazon Bedrock Converse API standard."""
        self.assertIn("toolSpec", AWS_TELEMETRY_TOOL_SPEC)
        spec = AWS_TELEMETRY_TOOL_SPEC["toolSpec"]
        self.assertEqual(spec["name"], AWS_TELEMETRY_TOOL_NAME)
        self.assertIn("description", spec)
        self.assertGreater(len(spec["description"]), 20)
        self.assertIn("inputSchema", spec)
        self.assertIn("json", spec["inputSchema"])
        schema = spec["inputSchema"]["json"]
        self.assertEqual(schema["type"], "object")
        self.assertIn("job_name", schema["properties"])
        self.assertIn("job_name", schema["required"])

    def test_telemetry_probe_execution_success(self):
        """Verify telemetry probe returns structured execution payload for enterprise job."""
        result = execute_telemetry_probe(job_name="FACETS_CLAIMS_LOAD", lookback_hours=24)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["job_name"], "FACETS_CLAIMS_LOAD")
        self.assertIn(result["status"], ["FAILED", "SUCCESS"])
        self.assertIn("duration_minutes", result)
        self.assertIn("sla_threshold_minutes", result)
        self.assertIn("cloudwatch_events", result)
        self.assertIsInstance(result["cloudwatch_events"], list)
        self.assertGreater(len(result["cloudwatch_events"]), 0)
        self.assertIn("s3_storage_checkpoint", result)

    def test_telemetry_probe_missing_job_name(self):
        """Verify tool handles missing job_name gracefully."""
        result = execute_telemetry_probe(job_name="")
        self.assertIn("error", result)
        self.assertEqual(result["status"], "INVALID_ARGUMENT")


if __name__ == "__main__":
    unittest.main()

"""AWS Telemetry and Diagnostic Tools for Amazon Bedrock Agents."""
from .tool_spec import AWS_TELEMETRY_TOOL_SPEC
from .telemetry_probe import execute_telemetry_probe

__all__ = ["AWS_TELEMETRY_TOOL_SPEC", "execute_telemetry_probe"]

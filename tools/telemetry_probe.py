"""
Tool Implementation: AWS Pipeline & CloudWatch Telemetry Probe.
This is the function invoked by the Amazon Bedrock Agent when handling tool calls.
"""

from typing import Dict, Any
from .mock_cloudwatch_service import CloudWatchTelemetryService

# Singleton service instance
_service = CloudWatchTelemetryService()

def execute_telemetry_probe(job_name: str, lookback_hours: int = 24, include_stack_trace: bool = True) -> Dict[str, Any]:
    """
    Executes the AWS Telemetry probe tool for Amazon Bedrock Converse API.
    
    Args:
        job_name: Name of the enterprise workflow job (from the 250 production jobs)
        lookback_hours: Hours of CloudWatch log stream telemetry to inspect
        include_stack_trace: Whether to include raw stack trace lines from CloudWatch
        
    Returns:
        Structured dictionary payload containing real execution telemetry, CloudWatch logs, and SLA stats.
    """
    if not job_name:
        return {
            "error": "Missing required parameter 'job_name'",
            "status": "INVALID_ARGUMENT"
        }
        
    telemetry = _service.query_job_telemetry(
        job_name=job_name,
        lookback_hours=lookback_hours,
        include_stack_trace=include_stack_trace
    )
    return telemetry

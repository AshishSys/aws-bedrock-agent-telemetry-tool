"""
Official Tool Specification for Amazon Bedrock Converse API and Bedrock Agents.
This adheres to the Amazon Bedrock Converse API toolConfig specification.
"""

AWS_TELEMETRY_TOOL_NAME = "query_aws_pipeline_telemetry"

AWS_TELEMETRY_TOOL_SPEC = {
    "toolSpec": {
        "name": AWS_TELEMETRY_TOOL_NAME,
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
                        "description": (
                            "The official enterprise job identifier to diagnose "
                            "(e.g., 'FACETS_CLAIMS_LOAD', 'FACETS_BILLING', 'Facets_Accounting', "
                            "'Facets_Capitation_Risk', 'FACETS_BRONZE_SILVER_GOLD')."
                        )
                    },
                    "lookback_hours": {
                        "type": "integer",
                        "description": "Number of hours of CloudWatch log stream telemetry to inspect. Default is 24."
                    },
                    "include_stack_trace": {
                        "type": "boolean",
                        "description": "Whether to extract and include full exception stack traces from CloudWatch log events. Default is True."
                    }
                },
                "required": ["job_name"]
            }
        }
    }
}

# Standard OpenAPI 3.0 specification for Amazon Bedrock Agents Action Groups
OPENAPI_ACTION_GROUP_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "AWS CloudWatch & Pipeline Telemetry Diagnostic API",
        "version": "1.0.0",
        "description": "API for querying live production job telemetry and CloudWatch logs for enterprise SLA management."
    },
    "paths": {
        "/diagnose-job": {
            "post": {
                "summary": "Retrieve CloudWatch telemetry and error diagnostics for a production workflow job",
                "description": "Returns execution status, error logs, and SLA impact for a specific job from the 250 enterprise jobs inventory.",
                "operationId": "diagnoseJob",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "job_name": {"type": "string", "example": "FACETS_CLAIMS_LOAD"},
                                    "lookback_hours": {"type": "integer", "default": 24},
                                    "include_stack_trace": {"type": "boolean", "default": True}
                                },
                                "required": ["job_name"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful diagnostic report",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "job_name": {"type": "string"},
                                        "status": {"type": "string"},
                                        "sla_breach_minutes": {"type": "number"},
                                        "error_signature": {"type": "string"},
                                        "cloudwatch_logs": {"type": "array", "items": {"type": "string"}},
                                        "s3_path": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

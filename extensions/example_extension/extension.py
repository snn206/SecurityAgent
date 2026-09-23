"""Example SecurityAgent extension."""
from __future__ import annotations
import structlog

logger = structlog.get_logger()


class ExampleExtension:
    """Reference extension — hooks into task lifecycle events."""

    async def on_task_start(self, execution_id: str, user_request: str, **kwargs) -> None:
        """Called when a task starts."""
        logger.info("extension.task_start", execution_id=execution_id, request=user_request[:50])

    async def on_report_generated(self, execution_id: str, report: dict, **kwargs) -> None:
        """Called when a report is generated — e.g. send notification, upload to S3."""
        logger.info("extension.report_generated", execution_id=execution_id,
                    findings=len(report.get("findings", [])))

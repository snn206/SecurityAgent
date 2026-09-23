"""Reports router — export reports."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response

from security_agent.execution.history import get_store
from security_agent.reports.exporters import HTMLExporter, JSONExporter, MarkdownExporter

router = APIRouter(tags=["reports"])


@router.get("/reports/{execution_id}")
async def get_report(execution_id: str, format: str = "json") -> Response:
    store = get_store()
    record = await store.get_execution(execution_id)
    if not record or not record.report:
        raise HTTPException(status_code=404, detail="Report not found")
    report = record.report
    match format:
        case "markdown" | "md":
            content = MarkdownExporter().export(report)
            return Response(
                content=content,
                media_type="text/markdown",
                headers={"Content-Disposition": f'attachment; filename="report_{execution_id}.md"'},
            )
        case "html":
            content = HTMLExporter().export(report)
            return Response(content=content, media_type="text/html")
        case _:
            content = JSONExporter().export(report)
            return Response(content=content, media_type="application/json")

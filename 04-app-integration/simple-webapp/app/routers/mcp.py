from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List

from ..services.mcp_client import McpClient, McpClientError

router = APIRouter(prefix="/mcp", tags=["mcp"])


class ToolInfo(BaseModel):
    name: str
    description: str | None = None


class ToolsListResponse(BaseModel):
    tools: List[ToolInfo]


class ActionRequest(BaseModel):
    params: Dict[str, Any] = Field(default_factory=dict)


class ActionResponse(BaseModel):
    tool: str
    data: Dict[str, Any]
    latency_ms: int
    success: bool = True


class ErrorResponse(BaseModel):
    error: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    server_type: str | None = None


def _client() -> McpClient:
    return McpClient()  # fresh each request; light-weight (mock)


@router.get("/tools", response_model=ToolsListResponse)
async def list_tools() -> ToolsListResponse:
    client = _client()
    try:
        tools = client.list_tools()
        return ToolsListResponse(tools=[ToolInfo(**t) for t in tools])
    except McpClientError as e:
        raise HTTPException(status_code=400, detail={"code": e.code, "message": e.message})


@router.post("/actions/{tool}", response_model=ActionResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def call_tool(tool: str, req: ActionRequest) -> ActionResponse:
    client = _client()
    try:
        data, latency_ms = client.call_tool(tool, req.params)
        return ActionResponse(tool=tool, data=data, latency_ms=latency_ms)
    except McpClientError as e:
        status = 404 if e.code == "tool_not_found" else 400
        raise HTTPException(status_code=status, detail={"code": e.code, "message": e.message, "detail": e.detail})


@router.get("/health", response_model=HealthResponse)
async def mcp_health() -> HealthResponse:
    client = _client()
    try:
        data = client.health()
        return HealthResponse(**data)
    except McpClientError as e:
        raise HTTPException(status_code=503, detail={"code": e.code, "message": e.message})

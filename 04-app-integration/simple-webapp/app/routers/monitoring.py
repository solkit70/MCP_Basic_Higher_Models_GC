"""
Monitoring Router - 모니터링 API 엔드포인트

이 모듈은 MCP 서버 모니터링을 위한 REST API 엔드포인트를 제공합니다.
- 시스템 상태 조회
- 성능 메트릭 조회
- 서버 헬스 체크
- 메트릭 리셋

작성일: 2025-12-14
작성자: Claude Sonnet 4.5 (Anthropic)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

from ..services.metrics_collector import get_metrics_collector
from ..services.health_checker import get_health_checker


router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# ============================================================
# Pydantic Models
# ============================================================

class ToolMetrics(BaseModel):
    """도구별 메트릭 데이터"""
    name: str
    total_calls: int
    success_calls: int
    error_calls: int
    success_rate: float
    avg_latency_ms: float
    min_latency_ms: int
    max_latency_ms: int
    last_call_time: Optional[str] = None


class MetricsSummary(BaseModel):
    """메트릭 요약"""
    total_calls: int
    total_successes: int
    total_errors: int
    success_rate: float
    avg_latency_ms: float


class ServerHealth(BaseModel):
    """서버 헬스 상태 (요약)"""
    name: str
    status: str  # ok | degraded | error
    type: str
    last_check: Optional[str] = None


class SystemStatusResponse(BaseModel):
    """시스템 상태 응답"""
    status: str
    timestamp: str
    uptime_seconds: int
    servers: List[ServerHealth]
    metrics_summary: MetricsSummary


class MetricsResponse(BaseModel):
    """메트릭 조회 응답"""
    timestamp: str
    uptime_seconds: int
    tools: List[ToolMetrics]


class HealthDetailResponse(BaseModel):
    """헬스 체크 상세 응답"""
    server_name: str
    server_type: str
    status: str
    last_check_time: Optional[str]
    last_success_time: Optional[str]
    consecutive_failures: int
    total_checks: int
    total_successes: int
    total_failures: int
    uptime_percentage: float
    response_time_ms: int
    server_info: Optional[dict] = None


class ResetRequest(BaseModel):
    """메트릭 리셋 요청"""
    confirm: bool = Field(default=True, description="확인 플래그")


class ResetResponse(BaseModel):
    """메트릭 리셋 응답"""
    success: bool
    message: str
    timestamp: str
    previous_metrics: MetricsSummary


class ErrorDetail(BaseModel):
    """에러 응답"""
    code: str
    message: str


# ============================================================
# API Endpoints
# ============================================================

@router.get(
    "/status",
    response_model=SystemStatusResponse,
    summary="시스템 상태 조회",
    description="전체 시스템의 현재 상태를 조회합니다 (서버 헬스, 메트릭 요약)"
)
async def get_system_status() -> SystemStatusResponse:
    """
    전체 시스템 상태 조회

    Returns:
        SystemStatusResponse: 시스템 상태 요약

    Example:
        ```bash
        curl http://localhost:8000/monitoring/status
        ```
    """
    collector = get_metrics_collector()
    checker = get_health_checker()

    # 메트릭 요약
    summary = collector.get_summary()
    metrics_summary = MetricsSummary(**summary)

    # 서버 헬스 상태
    all_health = checker.get_all_health_status()
    servers = [
        ServerHealth(
            name=h["server_name"],
            status=h["status"],
            type=h["server_type"],
            last_check=h["last_check_time"]
        )
        for h in all_health
    ]

    # 전체 상태 판단
    if not servers:
        overall_status = "no_servers"
    elif any(s.status == "error" for s in servers):
        overall_status = "error"
    elif any(s.status == "degraded" for s in servers):
        overall_status = "degraded"
    else:
        overall_status = "ok"

    return SystemStatusResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=collector.get_uptime_seconds(),
        servers=servers,
        metrics_summary=metrics_summary
    )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="성능 메트릭 조회",
    description="수집된 성능 메트릭 데이터를 조회합니다 (도구별 호출 횟수, 응답 시간 등)"
)
async def get_metrics(tool: Optional[str] = None) -> MetricsResponse:
    """
    성능 메트릭 조회

    Args:
        tool: 특정 도구 이름 (선택, 없으면 전체 조회)

    Returns:
        MetricsResponse: 메트릭 데이터

    Example:
        ```bash
        # 전체 메트릭
        curl http://localhost:8000/monitoring/metrics

        # 특정 도구
        curl http://localhost:8000/monitoring/metrics?tool=read_file
        ```
    """
    collector = get_metrics_collector()
    metrics_data = collector.get_metrics()

    # 도구 필터링
    if tool:
        tools = [t for t in metrics_data["tools"] if t["name"] == tool]
        if not tools:
            raise HTTPException(
                status_code=404,
                detail={"code": "tool_not_found", "message": f"Tool '{tool}' not found in metrics"}
            )
    else:
        tools = metrics_data["tools"]

    return MetricsResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=metrics_data["uptime_seconds"],
        tools=[ToolMetrics(**t) for t in tools]
    )


@router.get(
    "/health/{server}",
    response_model=HealthDetailResponse,
    summary="서버 헬스 체크",
    description="특정 MCP 서버의 헬스 상태를 상세히 조회합니다",
    responses={
        404: {
            "model": ErrorDetail,
            "description": "서버를 찾을 수 없음"
        }
    }
)
async def get_server_health(server: str) -> HealthDetailResponse:
    """
    특정 서버 헬스 체크

    Args:
        server: 서버 이름 (예: "file_server")

    Returns:
        HealthDetailResponse: 서버 헬스 상태 상세

    Raises:
        HTTPException: 서버를 찾을 수 없을 때 (404)

    Example:
        ```bash
        curl http://localhost:8000/monitoring/health/file_server
        ```
    """
    checker = get_health_checker()
    health = checker.get_health_status(server)

    if health is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "server_not_found", "message": f"Server '{server}' not found"}
        )

    return HealthDetailResponse(**health)


@router.post(
    "/reset",
    response_model=ResetResponse,
    summary="메트릭 리셋",
    description="수집된 모든 메트릭 데이터를 초기화합니다 (헬스 데이터는 유지)"
)
async def reset_metrics(request: ResetRequest = ResetRequest()) -> ResetResponse:
    """
    메트릭 리셋

    Args:
        request: 리셋 요청 (confirm=True 필요)

    Returns:
        ResetResponse: 리셋 결과 및 이전 메트릭 요약

    Example:
        ```bash
        curl -X POST http://localhost:8000/monitoring/reset \\
             -H "Content-Type: application/json" \\
             -d '{"confirm": true}'
        ```
    """
    if not request.confirm:
        raise HTTPException(
            status_code=400,
            detail={"code": "confirmation_required", "message": "Confirmation required to reset metrics"}
        )

    collector = get_metrics_collector()
    previous = collector.reset_metrics()

    return ResetResponse(
        success=True,
        message="Metrics reset successfully",
        timestamp=datetime.now(timezone.utc).isoformat(),
        previous_metrics=MetricsSummary(**previous)
    )


@router.get(
    "/health",
    response_model=List[HealthDetailResponse],
    summary="모든 서버 헬스 조회",
    description="모든 MCP 서버의 헬스 상태를 조회합니다"
)
async def get_all_server_health() -> List[HealthDetailResponse]:
    """
    모든 서버 헬스 조회

    Returns:
        List[HealthDetailResponse]: 모든 서버의 헬스 상태 리스트

    Example:
        ```bash
        curl http://localhost:8000/monitoring/health
        ```
    """
    checker = get_health_checker()
    all_health = checker.get_all_health_status()

    return [HealthDetailResponse(**h) for h in all_health]

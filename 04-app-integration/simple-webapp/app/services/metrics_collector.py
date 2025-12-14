"""
Metrics Collector - 성능 메트릭 수집 및 관리

이 모듈은 API 호출 메트릭을 수집하고 통계를 계산합니다.
- 인메모리 저장 (딕셔너리)
- 스레드 안전성 (Lock 사용)
- 도구별 통계 (호출 횟수, 응답 시간, 성공률)

작성일: 2025-12-14
작성자: Claude Sonnet 4.5 (Anthropic)
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class MetricsCollector:
    """
    API 호출 메트릭을 수집하고 관리하는 클래스

    Thread-safe한 메트릭 수집 및 조회를 제공합니다.

    Attributes:
        _metrics: 도구별 메트릭 데이터
        _lock: 스레드 안전성을 위한 Lock
        _start_time: 시스템 시작 시간 (초, UNIX timestamp)
    """

    def __init__(self) -> None:
        """메트릭 수집기 초기화"""
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._start_time = time.time()

    def record_call(
        self,
        tool: str,
        latency_ms: int,
        success: bool = True
    ) -> None:
        """
        API 호출을 기록합니다.

        Args:
            tool: 도구 이름 (예: "read_file", "list_files")
            latency_ms: 응답 시간 (밀리초)
            success: 성공 여부 (True=성공, False=실패)

        Example:
            >>> collector = MetricsCollector()
            >>> collector.record_call("read_file", 45, success=True)
            >>> collector.record_call("read_file", 120, success=False)
        """
        with self._lock:
            if tool not in self._metrics:
                self._metrics[tool] = {
                    "total_calls": 0,
                    "success_calls": 0,
                    "error_calls": 0,
                    "total_latency_ms": 0,
                    "min_latency_ms": float('inf'),
                    "max_latency_ms": 0,
                    "last_call_time": None
                }

            stats = self._metrics[tool]
            stats["total_calls"] += 1

            if success:
                stats["success_calls"] += 1
            else:
                stats["error_calls"] += 1

            stats["total_latency_ms"] += latency_ms
            stats["min_latency_ms"] = min(stats["min_latency_ms"], latency_ms)
            stats["max_latency_ms"] = max(stats["max_latency_ms"], latency_ms)
            stats["last_call_time"] = datetime.now(timezone.utc).isoformat()

    def get_metrics(self) -> Dict[str, Any]:
        """
        전체 메트릭 데이터를 조회합니다.

        Returns:
            메트릭 데이터 딕셔너리
            - uptime_seconds: 시스템 가동 시간
            - tools: 도구별 통계 리스트

        Example:
            >>> metrics = collector.get_metrics()
            >>> print(metrics["uptime_seconds"])
            3600
            >>> print(metrics["tools"][0]["name"])
            "read_file"
        """
        with self._lock:
            tools_data = []

            for tool_name, stats in self._metrics.items():
                # 통계 계산
                total_calls = stats["total_calls"]
                success_calls = stats["success_calls"]
                error_calls = stats["error_calls"]
                total_latency = stats["total_latency_ms"]

                # 성공률 계산
                success_rate = (
                    success_calls / total_calls
                    if total_calls > 0
                    else 0.0
                )

                # 평균 응답 시간 계산
                avg_latency = (
                    total_latency / total_calls
                    if total_calls > 0
                    else 0.0
                )

                # min/max 처리 (초기값 보정)
                min_latency = (
                    int(stats["min_latency_ms"])
                    if stats["min_latency_ms"] != float('inf')
                    else 0
                )

                tools_data.append({
                    "name": tool_name,
                    "total_calls": total_calls,
                    "success_calls": success_calls,
                    "error_calls": error_calls,
                    "success_rate": round(success_rate, 4),
                    "avg_latency_ms": round(avg_latency, 2),
                    "min_latency_ms": min_latency,
                    "max_latency_ms": stats["max_latency_ms"],
                    "last_call_time": stats["last_call_time"]
                })

            # 도구 이름순 정렬
            tools_data.sort(key=lambda x: x["name"])

            return {
                "uptime_seconds": self.get_uptime_seconds(),
                "tools": tools_data
            }

    def get_tool_stats(self, tool: str) -> Optional[Dict[str, Any]]:
        """
        특정 도구의 통계를 조회합니다.

        Args:
            tool: 도구 이름

        Returns:
            도구 통계 딕셔너리 또는 None (도구가 없을 경우)

        Example:
            >>> stats = collector.get_tool_stats("read_file")
            >>> if stats:
            ...     print(stats["success_rate"])
            0.9867
        """
        metrics = self.get_metrics()

        for tool_data in metrics["tools"]:
            if tool_data["name"] == tool:
                return tool_data

        return None

    def get_summary(self) -> Dict[str, Any]:
        """
        전체 메트릭 요약을 반환합니다.

        Returns:
            요약 통계 (총 호출, 성공, 에러, 성공률, 평균 응답시간)

        Example:
            >>> summary = collector.get_summary()
            >>> print(summary["total_calls"])
            200
            >>> print(summary["success_rate"])
            0.975
        """
        metrics = self.get_metrics()
        tools = metrics["tools"]

        if not tools:
            return {
                "total_calls": 0,
                "total_successes": 0,
                "total_errors": 0,
                "success_rate": 0.0,
                "avg_latency_ms": 0.0
            }

        # 전체 합계 계산
        total_calls = sum(t["total_calls"] for t in tools)
        total_successes = sum(t["success_calls"] for t in tools)
        total_errors = sum(t["error_calls"] for t in tools)

        # 가중 평균 응답 시간 계산
        total_latency = sum(
            t["avg_latency_ms"] * t["total_calls"]
            for t in tools
        )
        avg_latency = (
            total_latency / total_calls
            if total_calls > 0
            else 0.0
        )

        # 전체 성공률
        success_rate = (
            total_successes / total_calls
            if total_calls > 0
            else 0.0
        )

        return {
            "total_calls": total_calls,
            "total_successes": total_successes,
            "total_errors": total_errors,
            "success_rate": round(success_rate, 4),
            "avg_latency_ms": round(avg_latency, 2)
        }

    def reset_metrics(self) -> Dict[str, Any]:
        """
        모든 메트릭을 초기화합니다.

        Returns:
            리셋 전 메트릭 요약

        Example:
            >>> previous = collector.reset_metrics()
            >>> print(previous["total_calls"])
            200
            >>> # 이제 메트릭이 비어있음
        """
        with self._lock:
            previous_summary = self.get_summary()
            self._metrics = {}
            self._start_time = time.time()
            return previous_summary

    def get_uptime_seconds(self) -> int:
        """
        시스템 가동 시간을 초 단위로 반환합니다.

        Returns:
            가동 시간 (초)

        Example:
            >>> uptime = collector.get_uptime_seconds()
            >>> print(uptime)
            3600  # 1시간
        """
        return int(time.time() - self._start_time)

    def __repr__(self) -> str:
        """객체 문자열 표현"""
        summary = self.get_summary()
        return (
            f"MetricsCollector("
            f"uptime={self.get_uptime_seconds()}s, "
            f"calls={summary['total_calls']}, "
            f"success_rate={summary['success_rate']:.2%})"
        )


# 글로벌 싱글톤 인스턴스
_global_collector: Optional[MetricsCollector] = None
_collector_lock = threading.Lock()


def get_metrics_collector() -> MetricsCollector:
    """
    글로벌 메트릭 수집기 인스턴스를 반환합니다 (싱글톤 패턴).

    Returns:
        MetricsCollector 인스턴스

    Example:
        >>> from app.services.metrics_collector import get_metrics_collector
        >>> collector = get_metrics_collector()
        >>> collector.record_call("read_file", 45)
    """
    global _global_collector

    if _global_collector is None:
        with _collector_lock:
            # Double-checked locking
            if _global_collector is None:
                _global_collector = MetricsCollector()

    return _global_collector

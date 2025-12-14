"""
Health Checker - MCP 서버 헬스 상태 모니터링

이 모듈은 MCP 서버의 헬스 상태를 주기적으로 확인합니다.
- 백그라운드 스레드로 실행
- 타임아웃 감지
- 장애 상태 판단 및 기록

작성일: 2025-12-14
작성자: Claude Sonnet 4.5 (Anthropic)
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .mcp_client import McpClient, McpClientError, McpClientConfig


class HealthStatus:
    """헬스 상태 상수"""
    OK = "ok"
    DEGRADED = "degraded"
    ERROR = "error"


class HealthChecker:
    """
    MCP 서버의 헬스 상태를 주기적으로 확인하는 클래스

    백그라운드 스레드에서 주기적으로 MCP 서버를 체크하고
    상태를 추적합니다.

    Attributes:
        _health_data: 서버별 헬스 데이터
        _lock: 스레드 안전성을 위한 Lock
        _thread: 백그라운드 스레드
        _running: 실행 상태 플래그
        _interval: 체크 주기 (초)
    """

    def __init__(self, interval_seconds: int = 30) -> None:
        """
        헬스 체커 초기화

        Args:
            interval_seconds: 체크 주기 (기본 30초)

        Example:
            >>> checker = HealthChecker(interval_seconds=60)
            >>> checker.start_monitoring()
        """
        self._health_data: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._interval = interval_seconds

    def start_monitoring(self) -> None:
        """
        백그라운드 모니터링을 시작합니다.

        이미 실행 중이면 무시됩니다.

        Example:
            >>> checker = HealthChecker()
            >>> checker.start_monitoring()
            >>> # 백그라운드에서 주기적으로 헬스 체크 수행
        """
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="HealthChecker"
        )
        self._thread.start()

    def stop_monitoring(self) -> None:
        """
        백그라운드 모니터링을 중지합니다.

        Example:
            >>> checker.stop_monitoring()
            >>> # 백그라운드 스레드 종료
        """
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def _monitoring_loop(self) -> None:
        """
        백그라운드 모니터링 루프 (내부 메서드)

        주기적으로 _check_health()를 호출합니다.
        """
        while self._running:
            try:
                self._check_health()
            except Exception:
                # 헬스 체크 실패해도 루프는 계속 실행
                pass

            # interval 동안 대기 (작은 단위로 체크하여 빠른 종료 가능)
            for _ in range(self._interval):
                if not self._running:
                    break
                time.sleep(1)

    def _check_health(self) -> None:
        """
        MCP 서버의 헬스를 체크합니다 (내부 메서드).

        현재는 stdio mode의 file_server만 체크합니다.
        """
        # MCP 클라이언트 생성 (환경 변수 기반)
        try:
            config = McpClientConfig.from_env()
            server_name = self._get_server_name(config)

            # stdio 모드가 아니면 체크하지 않음
            if config.mode != "stdio":
                return

            # 헬스 체크 실행
            start_time = time.perf_counter()
            client = McpClient(config)

            try:
                health_result = client.health()
                response_time_ms = int((time.perf_counter() - start_time) * 1000)

                # 성공
                self._record_health_check(
                    server_name,
                    success=True,
                    response_time_ms=response_time_ms,
                    server_type=config.mode,
                    server_info=health_result
                )

            except McpClientError:
                # 실패
                response_time_ms = int((time.perf_counter() - start_time) * 1000)
                self._record_health_check(
                    server_name,
                    success=False,
                    response_time_ms=response_time_ms,
                    server_type=config.mode
                )

        except Exception:
            # 설정 오류 등으로 체크 불가능한 경우 무시
            pass

    def _get_server_name(self, config: McpClientConfig) -> str:
        """
        설정으로부터 서버 이름을 추출합니다.

        Args:
            config: MCP 클라이언트 설정

        Returns:
            서버 이름 (예: "file_server")
        """
        if config.mode == "stdio" and config.exec_path:
            # exec_path에서 서버 이름 추출 (예: "python file_server.py" → "file_server")
            parts = config.exec_path.split()
            if len(parts) >= 2:
                # 마지막 파라미터에서 확장자 제거
                filename = parts[-1]
                return filename.replace(".py", "").replace("\\", "/").split("/")[-1]
            return "stdio_server"
        elif config.mode == "ws" and config.server_uri:
            return "ws_server"
        else:
            return config.mode + "_server"

    def _record_health_check(
        self,
        server_name: str,
        success: bool,
        response_time_ms: int,
        server_type: str,
        server_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        헬스 체크 결과를 기록합니다 (내부 메서드).

        Args:
            server_name: 서버 이름
            success: 성공 여부
            response_time_ms: 응답 시간 (밀리초)
            server_type: 서버 타입 (stdio, ws 등)
            server_info: 서버 정보 (선택)
        """
        with self._lock:
            now = datetime.now(timezone.utc).isoformat()

            if server_name not in self._health_data:
                self._health_data[server_name] = {
                    "server_name": server_name,
                    "server_type": server_type,
                    "status": HealthStatus.OK,
                    "last_check_time": None,
                    "last_success_time": None,
                    "consecutive_failures": 0,
                    "total_checks": 0,
                    "total_successes": 0,
                    "total_failures": 0,
                    "response_time_ms": 0,
                    "server_info": None
                }

            data = self._health_data[server_name]
            data["last_check_time"] = now
            data["total_checks"] += 1
            data["response_time_ms"] = response_time_ms

            if success:
                data["total_successes"] += 1
                data["last_success_time"] = now
                data["consecutive_failures"] = 0
                data["server_info"] = server_info

                # 상태 업데이트 (error → degraded → ok)
                if data["status"] == HealthStatus.ERROR:
                    data["status"] = HealthStatus.DEGRADED
                elif data["status"] == HealthStatus.DEGRADED:
                    data["status"] = HealthStatus.OK

            else:
                data["total_failures"] += 1
                data["consecutive_failures"] += 1

                # 상태 업데이트 (ok → degraded → error)
                if data["consecutive_failures"] == 1:
                    data["status"] = HealthStatus.DEGRADED
                elif data["consecutive_failures"] >= 3:
                    data["status"] = HealthStatus.ERROR

    def get_health_status(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        특정 서버의 헬스 상태를 조회합니다.

        Args:
            server_name: 서버 이름

        Returns:
            헬스 상태 딕셔너리 또는 None (서버가 없을 경우)

        Example:
            >>> health = checker.get_health_status("file_server")
            >>> if health:
            ...     print(health["status"])  # "ok", "degraded", "error"
        """
        with self._lock:
            if server_name not in self._health_data:
                return None

            data = self._health_data[server_name].copy()

            # uptime_percentage 계산
            total_checks = data["total_checks"]
            total_successes = data["total_successes"]
            uptime_percentage = (
                (total_successes / total_checks * 100)
                if total_checks > 0
                else 100.0
            )
            data["uptime_percentage"] = round(uptime_percentage, 2)

            return data

    def get_all_health_status(self) -> List[Dict[str, Any]]:
        """
        모든 서버의 헬스 상태를 조회합니다.

        Returns:
            헬스 상태 딕셔너리 리스트

        Example:
            >>> all_health = checker.get_all_health_status()
            >>> for health in all_health:
            ...     print(f"{health['server_name']}: {health['status']}")
        """
        with self._lock:
            result = []
            for server_name in self._health_data:
                health = self.get_health_status(server_name)
                if health:
                    result.append(health)
            return result

    def is_monitoring(self) -> bool:
        """
        모니터링 중인지 여부를 반환합니다.

        Returns:
            모니터링 중이면 True, 아니면 False
        """
        return self._running

    def __repr__(self) -> str:
        """객체 문자열 표현"""
        all_health = self.get_all_health_status()
        return (
            f"HealthChecker("
            f"monitoring={self._running}, "
            f"servers={len(all_health)}, "
            f"interval={self._interval}s)"
        )


# 글로벌 싱글톤 인스턴스
_global_checker: Optional[HealthChecker] = None
_checker_lock = threading.Lock()


def get_health_checker() -> HealthChecker:
    """
    글로벌 헬스 체커 인스턴스를 반환합니다 (싱글톤 패턴).

    첫 호출 시 자동으로 모니터링을 시작합니다.

    Returns:
        HealthChecker 인스턴스

    Example:
        >>> from app.services.health_checker import get_health_checker
        >>> checker = get_health_checker()
        >>> health = checker.get_health_status("file_server")
    """
    global _global_checker

    if _global_checker is None:
        with _checker_lock:
            # Double-checked locking
            if _global_checker is None:
                _global_checker = HealthChecker(interval_seconds=30)
                _global_checker.start_monitoring()

    return _global_checker

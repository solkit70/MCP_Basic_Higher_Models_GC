"""
Quick test script for M8 Capstone monitoring system

This script tests the monitoring components without starting the full server.
"""

import sys
from pathlib import Path

# Add app to path
app_root = Path(__file__).parent.parent.parent / "04-app-integration" / "simple-webapp"
sys.path.insert(0, str(app_root))

print("=" * 60)
print("M8 Capstone - Quick Validation Test")
print("=" * 60)
print()

# Test 1: Import MetricsCollector
print("[Test 1] Importing MetricsCollector...")
try:
    from app.services.metrics_collector import MetricsCollector, get_metrics_collector
    print("[OK] MetricsCollector imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import MetricsCollector: {e}")
    sys.exit(1)

# Test 2: Create collector and record metrics
print("\n[Test 2] Recording metrics...")
try:
    collector = MetricsCollector()
    collector.record_call("test_tool", latency_ms=45, success=True)
    collector.record_call("test_tool", latency_ms=30, success=True)
    collector.record_call("test_tool", latency_ms=60, success=False)

    metrics = collector.get_metrics()
    tools = metrics["tools"]

    assert len(tools) == 1, f"Expected 1 tool, got {len(tools)}"
    assert tools[0]["name"] == "test_tool"
    assert tools[0]["total_calls"] == 3
    assert tools[0]["success_calls"] == 2
    assert tools[0]["error_calls"] == 1

    print(f"[OK] Metrics recorded successfully")
    print(f"  - Total calls: {tools[0]['total_calls']}")
    print(f"  - Success rate: {tools[0]['success_rate']:.2%}")
    print(f"  - Avg latency: {tools[0]['avg_latency_ms']:.1f}ms")
except Exception as e:
    print(f"[FAIL] Failed to record metrics: {e}")
    sys.exit(1)

# Test 3: Import HealthChecker
print("\n[Test 3] Importing HealthChecker...")
try:
    from app.services.health_checker import HealthChecker, get_health_checker
    print("[OK] HealthChecker imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import HealthChecker: {e}")
    sys.exit(1)

# Test 4: Create health checker
print("\n[Test 4] Creating HealthChecker...")
try:
    checker = HealthChecker(interval_seconds=60)
    print(f"[OK] HealthChecker created successfully")
    print(f"  - Monitoring: {checker.is_monitoring()}")
    print(f"  - Interval: 60s")
except Exception as e:
    print(f"[FAIL] Failed to create HealthChecker: {e}")
    sys.exit(1)

# Test 5: Import MonitoringRouter
print("\n[Test 5] Importing MonitoringRouter...")
try:
    from app.routers.monitoring import router, SystemStatusResponse, MetricsResponse
    print("[OK] MonitoringRouter imported successfully")
    print(f"  - Router prefix: {router.prefix}")
    print(f"  - Router tags: {router.tags}")
except Exception as e:
    print(f"[FAIL] Failed to import MonitoringRouter: {e}")
    sys.exit(1)

# Test 6: Test main app integration
print("\n[Test 6] Testing FastAPI app integration...")
try:
    from app.main import app as fastapi_app

    # Check if monitoring router is included
    routes = [route.path for route in fastapi_app.routes]
    monitoring_routes = [r for r in routes if r.startswith("/monitoring")]

    assert len(monitoring_routes) > 0, "No monitoring routes found"

    print(f"[OK] FastAPI app integrated successfully")
    print(f"  - App title: {fastapi_app.title}")
    print(f"  - App version: {fastapi_app.version}")
    print(f"  - Monitoring routes: {len(monitoring_routes)}")

    # Show monitoring routes
    for route in monitoring_routes:
        print(f"    - {route}")

except Exception as e:
    print(f"[FAIL] Failed to test app integration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("All tests passed! [OK]")
print("=" * 60)
print()
print("Summary:")
print("  [OK] MetricsCollector: Working")
print("  [OK] HealthChecker: Working")
print("  [OK] MonitoringRouter: Working")
print("  [OK] FastAPI Integration: Working")
print()
print("M8 Capstone monitoring system is ready!")
print()

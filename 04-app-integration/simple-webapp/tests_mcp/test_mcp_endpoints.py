import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_tools():
    r = client.get("/mcp/tools")
    assert r.status_code == 200
    data = r.json()
    assert "tools" in data
    names = {t["name"] for t in data["tools"]}
    assert "echo" in names and "sum" in names


def test_call_tool_echo():
    payload = {"params": {"message": "hello"}}
    r = client.post("/mcp/actions/echo", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["tool"] == "echo"
    assert body["data"]["echo"]["message"] == "hello"
    assert isinstance(body["latency_ms"], int)


def test_call_tool_sum():
    payload = {"params": {"numbers": [1, 2, 3.5]}}
    r = client.post("/mcp/actions/sum", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["sum"] == 6.5


def test_call_tool_sum_validation_error():
    # numbers is not a list
    payload = {"params": {"numbers": "oops"}}
    r = client.post("/mcp/actions/sum", json=payload)
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert detail["code"] == "validation_error"


def test_tool_not_found():
    r = client.post("/mcp/actions/unknown_tool", json={"params": {}})
    assert r.status_code == 404
    detail = r.json()["detail"]
    assert detail["code"] == "tool_not_found"


def test_mcp_health():
    r = client.get("/mcp/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["server_type"] == "mock"

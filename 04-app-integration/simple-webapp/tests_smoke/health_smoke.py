import json
from datetime import datetime

try:
    # Import the FastAPI app directly
    from app.main import app
except Exception as e:
    print("IMPORT_ERROR:", repr(e))
    raise

try:
    from fastapi.testclient import TestClient
except Exception as e:
    print("DEPENDENCY_ERROR:", repr(e))
    raise


def main() -> int:
    client = TestClient(app)
    resp = client.get("/health")
    ok = resp.status_code == 200
    payload = {}
    try:
        payload = resp.json()
    except Exception:
        payload = {"raw_text": resp.text}

    out = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status_code": resp.status_code,
        "ok": ok,
        "json": payload,
    }
    print(json.dumps(out, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
